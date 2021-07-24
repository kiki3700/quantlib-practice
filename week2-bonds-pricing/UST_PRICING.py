#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 14:58:53 2021

@author: ben
"""

import QuantLib as ql
from UST_CURVE import GET_DATE, GET_QUOTE, TREASURY_CURVE

# Basic setup
eval_date = GET_DATE()
quote = GET_QUOTE(eval_date)
curve = TREASURY_CURVE(eval_date, quote)

# handl , engine
curveHandle = ql.YieldTermStructureHandle(curve)
bondEngine = ql.DiscountingBondEngine(curveHandle)

# Treasury bond information
issueDate =ql.Date(13,11,2020)
maturityDate =ql.Date(13,11,2030)
tenor = ql.Period(ql.Semiannual)
calendar = ql.UnitedStates()
convention = ql.ModifiedFollowing
dateGeneration = ql.DateGeneration.Backward
endOfMonth = False
schedule = ql.Schedule(issueDate,
                     maturityDate,
                     tenor,
                     calendar,
                     convention,
                     convention,
                     dateGeneration,
                     endOfMonth)
settlementDays = 1 # after trade when settlement
faceAmount = 100
coupon = [0.0175]
dayCounter = ql.ActualActual() 

#Fixed rate bond
fixedRateBond = ql.FixedRateBond(settlementDays,
                                 faceAmount,
                                 schedule,
                                 coupon,
                                 dayCounter)

# conduct pricing
fixedRateBond.setPricingEngine(bondEngine)

# print pricing result
clean_price = fixedRateBond.cleanPrice() #clean_price => without coupon because of trade = derty price = cleanprice + coupon
accrued_interest = fixedRateBond.accruedAmount()
dirty_price = fixedRateBond.dirtyPrice()
ytm = fixedRateBond.bondYield(dayCounter, ql.Compounded, ql.Semiannual)

print("clean price = {}".format(clean_price))
print("accrued interest = {}".format(accrued_interest))
print('dirty price = {}'.format(dirty_price))
print("Yield to maturiry ={}".format(ytm))

#Generate cashflow table
for cashflow in fixedRateBond.cashflows():
    print(cashflow.date(), cashflow.amount())
    
#calculatie YTM
new_ytm = ql.InterestRate(fixedRateBond.bondYield(dayCounter,
                                                  ql.Compounded,
                                                  ql.Semiannual),
                          dayCounter,
                          ql.Compounded,
                          ql.Semiannual)

#Duration&convexity
duration = ql.BondFunctions.duration(fixedRateBond, new_ytm)
convexity = ql.BondFunctions.convexity(fixedRateBond, new_ytm)

print("DUration = {}".format(duration))
print("convexity = {}".format(convexity))