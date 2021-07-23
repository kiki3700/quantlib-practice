# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
""" 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import QuantLib as ql
from bs4 import BeautifulSoup
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('headless') #백단에서 구동되게 만드는 것이다.^^

###ㅎㅁ수 만들기
def GET_DATE():
    date = ql.Date().todaysDate() # todays date
    one_day = ql.Period(1,ql.Days)
    last_bday =date - one_day
    
    us = ql.UnitedStates()
    while us.isBusinessDay(last_bday)==False:
        last_bday -= one_day
        
    date = datetime.date(last_bday.year(), last_bday.month(), last_bday.dayOfMonth())
    
    return date

def GET_QUOTE(eval_date):
    driver = webdriver.Chrome('/home/ben/chromedriver',options=options)
    tenors = ['01M', '03M', '06M', '01Y', '02Y', '03Y', '05Y', '07Y', '10Y', '30Y']
    
    ## Create Empty Lists
    maturities = []
    days =[]
    prices=[]
    coupons = []
    ## GET market information
    for i, tenor in enumerate(tenors):
        driver.get('https://www.wsj.com/market-data/quotes/bond/BX/TMUBMUSD'+tenor+'?mod=md_bond_overview_quote')
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        #price
        if i <= 3:
            data_src = soup.find("span", id="quote_val")
            price = data_src.text
            price = float(price[:-1])
        else:
            data_src = soup.find("span", id="price_quote_val")
            price = data_src.text
            price = price.split()
            price1= float(price[0])
            price = price[1].split('/')
            price2 = float(price[0])
            price3 = float(price[1])
            price = price1+price2/price3
        
        #coupon
        data_src2 = soup.find_all("span", class_="data_data")
        coupon = data_src2[2].text
        if coupon != '':
            coupon = float(coupon[:-1])
        else:
            coupon = 0.0
        # Maturity Date
        maturity = data_src2[3].text
        maturity = datetime.datetime.strptime(maturity, '%m/%d/%y').date()
        
        # send to list
        days.append((maturity - eval_date).days)
        prices.append(price)
        coupons.append(coupon)
        maturities.append(maturity)
    
    #create data frame
    df = pd.DataFrame([maturities, days, prices, coupons]).transpose() # trans pose는 
    headers = ['maturity', 'days', 'price', 'coupon']
    df.columns = headers
    df.set_index('maturity', inplace = True)
    return df

def TREASURY_CURVE(eval_date, rate_table):
    
    #Divide Quotes
    tbill = rate_table[0:4]
    tbond = rate_table[4:]
    
    # set evaluation Date
    eval_date = ql.Date(eval_date.day, eval_date.month, eval_date.year)
    ql.Settings.instance().evaluationDate = eval_date
    
    #Set market Convention
    calendar =ql.UnitedStates()
    convention = ql.ModifiedFollowing
    dayCounter = ql.ActualActual()
    endOfMonth = False
    fixingDays = 1 #when fix rate => one day ago
    faceAmount = 100
    frequency = ql.Period(ql.Semiannual)
    dateGeneration = ql.DateGeneration.Backward
    
    # Construct Treasury bill helpers
    bill_helpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(price/100.0)),
                                          ql.Period(maturity, ql.Days),
                                          fixingDays,
                                          calendar,
                                          convention,
                                          endOfMonth,
                                          dayCounter)
                     for price, maturity in zip(tbill['price'], tbill['days'])]
    
    # Consturct Treasury bonds helpers
    bond_helpers = []
    for price, coupon, maturity in zip(tbond['price'], tbond['coupon'], tbond['days']):
        maturity_date = eval_date + ql.Period(maturity, ql.Days)
        schedule = ql.Schedule(eval_date,
                                maturity_date,
                                frequency,
                                calendar,
                                convention,
                                convention,
                                dateGeneration,
                                endOfMonth)
        bond_helper = ql.FixedRateBondHelper(ql.QuoteHandle(ql.SimpleQuote(price)),
                                            fixingDays,
                                            faceAmount,
                                            schedule,
                                            [coupon/100.0],
                                            dayCounter,
                                            convention)
        bond_helpers.append(bond_helper)
    #bind helper
    rate_helper = bill_helpers+bond_helpers
    
    #boild curve 
    curve = ql.PiecewiseLinearZero(eval_date,
                                   rate_helper,
                                   dayCounter)
    
    return curve

def DISCOUNT_FACTOR(date, curve):
    date = ql.Date(date.day, date.month, date.year)
    discount_factor = curve.discount(date)
    return discount_factor

def ZERO_RATE(date, curve):
    date = ql.Date(date.day, date.month, date.year)
    dayCount = ql.ActualActual()
    compounding = ql.Compounded
    frequency = ql.Continuous
    zero_rate = curve.zeroRate(date, dayCount, compounding, frequency).rate()
    return zero_rate
    
    
if __name__=="__main__":
    eval_date = GET_DATE()
    rate_table = GET_QUOTE(eval_date)
    curve = TREASURY_CURVE(eval_date, rate_table)
    
    rate_table['discount factor'] = np.nan
    rate_table['zero rate'] = np.nan
    
    for date in rate_table.index:
        rate_table.loc[date, 'discount factor']=DISCOUNT_FACTOR(date, curve)
        rate_table.loc[date, 'zero rate'] = ZERO_RATE(date, curve)
        
    #print(rate_table[['discount factor', 'zero rate']])
    
    #Visualization
    plt.figure(figsize=(10,8))
    plt.plot(rate_table['zero rate'],'b.-')
    plt.title('Zero Curve', loc ='center')
    plt.xlabel('maturity')
    plt.ylabel('zro rate')
    
    plt.figure(figsize=(10, 8))
    plt.plot(rate_table['discount factor'],'r.-')
    plt.title("dicount foctor', loc = 'center")
    plt.xlabel("maturity")
    plt.ylabel("dicount factor")
    