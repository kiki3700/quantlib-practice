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
    driver = webdriver.Chrome('C:\chromedriver',options=options)
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

if __name__=="__main__":
    eval_date = GET_DATE()
    rate_table = GET_QUOTE(eval_date)
    