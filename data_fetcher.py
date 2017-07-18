# Import required libraries
import datetime as dt

import numpy as np
import pandas as pd
from pandas_datareader.data import Options
from py_vollib.black_scholes_merton.implied_volatility import *

from trading_calendar import USTradingCalendar


# Get time delta
def get_time_delta(today, date_list, trading_calendar=True):

    delta_list = []

    if trading_calendar:
        year = 252
        calendar = USTradingCalendar()

        for date in date_list:
            trading_holidays = calendar.holidays(today, date).tolist()
            delta = np.busday_count(today, date, holidays=trading_holidays) + 1
            delta_list.append(delta)
    else:
        year = 365

        for date in date_list:
            delta = abs((today - date).days) + 1
            delta_list.append(delta)

    delta_list = np.array(delta_list)
    normalized = delta_list / float(year)

    return delta_list, normalized


# Get tape
def get_raw_data(ticker):
    tape = Options(ticker, 'yahoo')
    data = tape.get_all_data()
    return data


# Get volatility matrix
def get_filtered_data(data, calculate_iv=True, call=True, put=False,
                      volume_threshold=1, above_below=False,
                      rf_interest_rate=0.0, dividend_rate=0.0,
                      trading_calendar=True, market=True):

    if call and put:
        raise Exception('Must specify either call or put.')
    if not call and not put:
        raise Exception('Must specify either call or put.')
    if call:
        flag = 'c'
        typ = 'call'
    if put:
        flag = 'p'
        typ = 'put'

    if not above_below:
        above_below = 1E9  # Very large number, good enough for our purposes

    underlying = data['Underlying_Price'][0]

    # Filter dataframe
    df = data[(data.index.get_level_values('Type') == typ)
              & (data['Vol'] >= volume_threshold)
              & (data.index.get_level_values('Strike') < (underlying + above_below + 1))
              & (data.index.get_level_values('Strike') > (underlying - above_below - 1))]

    # Get columns
    if typ == 'call':
        premiums = df['Ask']  # Always assume user wants to get filled price
    else:
        premiums = df['Bid']

    if not market:
        premiums = df['Last']  # Last executed price vs Bid/Ask price

    strikes = df.index.get_level_values('Strike').values
    expiries = df.index.get_level_values('Expiry').to_pydatetime()
    plotting, time_to_expirations = get_time_delta(dt.datetime.today(
    ), expiries, trading_calendar)  # Can get slow if too many expiries
    ivs = df['IV'].values

    # Make sure nothing thows up
    assert len(premiums) == len(strikes)
    assert len(strikes) == len(time_to_expirations)

    if calculate_iv:

        sigmas = []
        for premium, strike, time_to_expiration in zip(premiums, strikes, time_to_expirations):

            # Constants
            P = premium
            S = underlying
            K = strike
            t = time_to_expiration
            r = rf_interest_rate / 100
            q = dividend_rate / 100
            try:
                sigma = implied_volatility(P, S, K, t, r, q, flag)
                sigmas.append(sigma)
            except:
                sigma = 0.0
                sigmas.append(sigma)

        ivs = np.array(sigmas)

    return strikes, plotting, ivs
