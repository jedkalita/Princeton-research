import math
import numpy as np
from scipy.stats import rv_discrete
import threading
import time
import logging
import random
import matplotlib.pyplot as plt

s = np.random.poisson(5, 1000000)
#print(s)
count, bins, ignored = plt.hist(s, 14, normed=True)
#plt.show()

def nextTime(rateParameter):
    return -math.log(1.0 - random.random()) / rateParameter

#print(nextTime(1/40.0))
#number of shares will be in unit size
#Market Orders - Buy/Sell
#Limit Orders - Buy/Sell
#Cancellation Orders for for placed limit orders
#Price scale will be price
#time-scale will be milliseconds
dp = 1 #the tick size on the price - unit price difference
orders = 1 #the order size - unit
market_order_rate_buy = 2 #units of shares/ms time
market_order_rate_sell = 2 #units of shares/ms time
limit_order_rate_buy = 3 #units of shares/price(log) time(ms)
limit_order_rate_sell = 3 #units of shares/price(log) time(ms)
order_cancellation_rate = 0.1 #units of 1/time(ms) - 1 cancelled every 10 ms on average
#now make poisson processes for each of the 5 processes -
#Market Order Buy, Market Order Sell, Limit Order Buy, Limit Order Sell, Order Cancel
#they will each generate the next time step, and then for the earliest time, if it is a
#limit order, project it onto the (log) price dimension, spaced at every dp intervals








