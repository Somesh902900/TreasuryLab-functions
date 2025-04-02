from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

def calculate_bond_cashflows(face_value, coupon_rate, maturity_date, settlement_date, frequency=2):
    """
    Generates bond cash flows and corresponding time periods.
    Uses the 360/360 day count convention.
    """
    maturity_date = datetime.strptime(maturity_date, "%Y-%m-%d")
    settlement_date = datetime.strptime(settlement_date, "%Y-%m-%d")
    
    coupon_payment = (coupon_rate / 100) * face_value / frequency
    months_between_coupons = 12 // frequency
    next_coupon_date = maturity_date
    
    while next_coupon_date > settlement_date:
        prev_coupon_date = next_coupon_date
        next_coupon_date = next_coupon_date - relativedelta(months=months_between_coupons)
    
    prev_coupon_date, next_coupon_date = next_coupon_date, prev_coupon_date
    
    days_to_next_coupon = ((next_coupon_date.year - settlement_date.year) * 360 +
                           (next_coupon_date.month - settlement_date.month) * 30 +
                           (next_coupon_date.day - settlement_date.day))
    tenor_first = days_to_next_coupon / 360
    
    num_periods = int(((maturity_date.year - next_coupon_date.year) * frequency) +
                      ((maturity_date.month - next_coupon_date.month) // (12 // frequency)) + 1)
    
    tenors = [tenor_first + (i / frequency) for i in range(num_periods)]
    cash_flows = [coupon_payment] * num_periods
    cash_flows[-1] += face_value  
    
    return cash_flows, tenors

def calculate_price(face_value, coupon_rate, maturity_date, settlement_date, ytm, frequency=2):
    """
    Computes bond price using the discounted cash flow approach.
    """
    cash_flows, tenors = calculate_bond_cashflows(face_value, coupon_rate, maturity_date, settlement_date, frequency)
    discount_factors = [(1 / (1 + ytm / 100 / frequency) ** (t * frequency)) for t in tenors]
    
    return sum(cf * df for cf, df in zip(cash_flows, discount_factors))

def calculate_macaulay_duration(face_value, coupon_rate, maturity_date, settlement_date, ytm, frequency=2):
    """
    Computes Macaulay Duration.
    """
    cash_flows, tenors = calculate_bond_cashflows(face_value, coupon_rate, maturity_date, settlement_date, frequency)
    price = calculate_price(face_value, coupon_rate, maturity_date, settlement_date, ytm, frequency)
    discount_factors = [(1 / (1 + ytm / 100 / frequency) ** (t * frequency)) for t in tenors]
    
    discounted_cf = [cf * df for cf, df in zip(cash_flows, discount_factors)]
    weighted_sum = sum(t * cf for t, cf in zip(tenors, discounted_cf))
    
    return weighted_sum / sum(discounted_cf)

def calculate_modified_duration(macaulay_duration, ytm, frequency=2):
    """
    Computes Modified Duration.
    """
    return macaulay_duration / (1 + (ytm / 100 / frequency))

def calculate_pv01(modified_duration, price):
    """
    Computes PV01 (Price Value of a Basis Point).
    """
    return (modified_duration * price) / 10_000

def compute_sensitivity_measures(face_value, coupon_rate, maturity_date, settlement_date, ytm, frequency=2):
    """
    Computes Macaulay Duration, Modified Duration, and PV01 for a bond.
    """
    price = calculate_price(face_value, coupon_rate, maturity_date, settlement_date, ytm, frequency)
    macaulay_duration = calculate_macaulay_duration(face_value, coupon_rate, maturity_date, settlement_date, ytm, frequency)
    modified_duration = calculate_modified_duration(macaulay_duration, ytm, frequency)
    pv01 = calculate_pv01(modified_duration, price)
    
    return {
        "Price": round(price, 4),
        "Macaulay Duration": round(macaulay_duration, 4),
        "Modified Duration": round(modified_duration, 4),
        "PV01": round(pv01, 6)
    }

sensitivity = compute_sensitivity_measures(
    face_value=100,
    coupon_rate=7.46,
    maturity_date="2017-08-28",
    settlement_date="2004-01-15",
    ytm=5.4621
)

print(sensitivity)




