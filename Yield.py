#!/usr/bin/env python
# coding: utf-8

# In[16]:


from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.optimize import newton

def bond_ytm(face_value, coupon_rate, clean_price, maturity_date, settlement_date, frequency=2):

    maturity_date = datetime.strptime(maturity_date, "%Y-%m-%d")
    settlement_date = datetime.strptime(settlement_date, "%Y-%m-%d")

    coupon_payment = (coupon_rate / 100) * face_value / frequency

    months_between_coupons = 12 // frequency
    next_coupon_date = maturity_date

    while next_coupon_date > settlement_date:
        prev_coupon_date = next_coupon_date
        next_coupon_date = next_coupon_date - relativedelta(months=months_between_coupons)

    prev_coupon_date, next_coupon_date = next_coupon_date, prev_coupon_date

    #print(f"Previous Coupon Date: {prev_coupon_date}, Next Coupon Date: {next_coupon_date}")

    days_to_next_coupon = ((next_coupon_date.year - settlement_date.year) * 360 +
                           (next_coupon_date.month - settlement_date.month) * 30 +
                           (next_coupon_date.day - settlement_date.day))

    tenor_first = days_to_next_coupon / 360
    #print(f"Days to Next Coupon: {days_to_next_coupon}, Tenor First: {tenor_first}")

    num_periods = int(((maturity_date.year - next_coupon_date.year) * frequency) +
                      ((maturity_date.month - next_coupon_date.month) // (12 // frequency)) + 1)

    tenors = [tenor_first + (i / frequency) for i in range(num_periods)]
    #print(f"Tenors: {tenors}")

    cash_flows = [coupon_payment] * num_periods
    cash_flows[-1] += face_value
    #print(f"Cash Flows: {cash_flows}")

    days_since_last_coupon = ((settlement_date.year - prev_coupon_date.year) * 360 +
                              (settlement_date.month - prev_coupon_date.month) * 30 +
                              (settlement_date.day - prev_coupon_date.day))

    accrued_interest = (coupon_payment * days_since_last_coupon) / 180
    #print(f"Accrued Interest: {accrued_interest}")

    dirty_price = clean_price + accrued_interest
    #print(f"Dirty Price: {dirty_price}")

    def ytm_function(y):
        discount_factors = [(1 / (1 + y / frequency) ** (t * frequency)) for t in tenors]
        discounted_cash_flows = [cf * df for cf, df in zip(cash_flows, discount_factors)]
        return sum(discounted_cash_flows) - dirty_price 

    initial_guess = (coupon_rate) / 100

    ytm_solution = newton(ytm_function, initial_guess) * 100

    return round(ytm_solution, 4)


# In[ ]:





# In[ ]:




