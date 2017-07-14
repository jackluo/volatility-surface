import os
import sys
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

from vollib.black_scholes_merton.implied_volatility import *

# TODO: Dynamically scrape the QuoteData for all tickers in a list
folder = r"volatilities"
quote_data = "QuoteData.dat"

# Sets minimum volume to filter the options
volume_threshold = 100
rf_interest_rate = 0.01
dividend_rate = 0.03

# TODO: Change calendar to a 252 day trading calendar
cumulative_month = {'Jan': 31, 'Feb': 57, 'Mar': 90,
                    'Apr': 120, 'May': 151, 'Jun': 181,
                    'Jul': 212, 'Aug': 243, 'Sep': 273,
                    'Oct': 304, 'Nov': 334, 'Dec': 365}


def get_time_to_expiration(string):

    string = string.split()
    expiration_year, expiration_month = string[0], string[1]
    expiration_date = (int(expiration_year) - (int(current_year) %
                                               2000)) * 365 + cumulative_month[expiration_month] - 7
    return expiration_date - current_date


def get_strike(string):

    string = string.split()
    strike = float(string[2])
    return strike


def calculate_iv(bid, ask, strike, time_to_expiration, flag, direction):

    # Select which value to use for premium
    if "long" in direction:
        premium = float(bid)
    elif "short" in direction:
        premium = float(ask)
    elif "average" in direction:
        premium = (float(bid) + float(ask)) / 2.0
    else:
        print "Check code as direction parameter is neither long, short, or average"
        exit(1)

    time_to_expiration /= 365.0

    # Convert to textbook shorthand notation
    P = premium
    S = underlying
    K = strike
    t = time_to_expiration
    r = rf_interest_rate
    q = dividend_rate

    # Fastest method to calculate implied volatility, using the vollib library
    sigma = implied_volatility(P, S, K, t, r, q, flag)

    return max(sigma, 0.0)


# Opens CBOE QuoteData
try:
    data = open(quote_data)
    header1 = data.readline().split(",")
    header2 = data.readline().split(",")
    date = header2[0].split()
    data.close()
except:
    print "Couldn't read QuoteData. Maybe the format changed?"
    exit(1)

# Parse the header information in QuotaData
ticker = header1[0].split()[0]
underlying = float(header1[1])
current_month, current_day, current_year = date[0], date[1], date[2]
current_date = cumulative_month[current_month] + int(current_day) - 30

# Prints visual information
print "Calculating implied volatilities"
print "Stock: %s @ %s$" % (ticker, underlying)
print "Date: %s %s %s (%sth day)" % (current_month, current_day, current_year, current_date)
# print ""
# print header1
# print header2
# print date
# print ""

# Opens CBOE quotedata to get calls, and fills in NA values with 0.0, and
# duplicates it for puts
df = pd.read_csv(quote_data, sep=",", header=2,
                 mangle_dupe_cols=True, encoding="utf-8", engine="c")
df2 = df

# Munge data by dropping useless columns, filling blank values and taking
# only options that have nonzero volume (eg that actually sell)
keep = ["Calls", "Bid", "Ask", "Vol"]
df = df[keep]
df = df.fillna(0.0)

df = df[df["Bid"] != 0.0]
df = df[df["Ask"] != 0.0]
# df = df[df["Vol"] > volume_threshold]

# Get expiration dates and strike prices
expirations = df["Calls"].apply(get_time_to_expiration)
expirations.name = "Expiration"

strikes = df["Calls"].apply(get_strike)
strikes.name = "Strike"

df = df.join(expirations).join(strikes)

print "Calculating implied volatility for calls"

call_ivs = []
for index, row in df.iterrows():
    # print repr(row["Bid"]), repr(row["Ask"]),
    # repr(row["Strike"]),repr(row["Expiration"])
    iv = calculate_iv(row["Bid"],
                      row["Ask"],
                      row["Strike"],
                      row["Expiration"],
                      "c", "average")
    call_ivs.append(iv)

df["Call IV"] = call_ivs
print "Calculated implied volatility for %d calls" % len(df.index)


# Repeat for put options data
# Notice the .1 for repeated names
keep2 = ["Puts", "Bid.1", "Ask.1", "Vol.1"]
df2 = df2[keep2]
df2 = df2.fillna(0.0)

df2 = df2[df2["Bid.1"] != 0.0]
df2 = df2[df2["Ask.1"] != 0.0]
# df2 = df2[df2["Vol.1"] > volume_threshold]

# Get expiration dates and strike prices
expirations = df2["Puts"].apply(get_time_to_expiration)
expirations.name = "Expiration"

strikes = df2["Puts"].apply(get_strike)
strikes.name = "Strike"

df2 = df2.join(expirations).join(strikes)

print "Calculating implied volatility for puts"

put_ivs = []
for index, row in df2.iterrows():
    # print repr(row["Bid.1"]), repr(row["Ask.1"]),
    # repr(row["Strike"]),repr(row["Expiration"])
    iv = calculate_iv(row["Bid.1"],
                      row["Ask.1"],
                      row["Strike"],
                      row["Expiration"],
                      "p", "average")
    put_ivs.append(iv)

df2["Put IV"] = put_ivs
df2.rename(columns={"Bid.1": 'Bid', "Ask.1": "Ask",
                    "Vol.1": "Vol"}, inplace=True)
print "Calculated implied volatility for %d puts" % len(df2.index)


# Output both calls and puts
try:
    os.makedirs(folder)
except OSError:
    if not os.path.isdir(folder):
        raise

df.to_csv(os.path.join(folder, ticker + r"_calls.csv"),
          sep=",", encoding='utf-8')
df2.to_csv(os.path.join(folder, ticker + r"_puts.csv"),
           sep=",", encoding='utf-8')
print "Done!"
