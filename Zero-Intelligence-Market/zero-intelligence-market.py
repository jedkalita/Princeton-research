import math
import numpy as np
from scipy.stats import rv_discrete
import threading
import time
import logging
import random
import matplotlib.pyplot as plt
from limit_order import *

s = np.random.poisson(5, 1000000)
#print(s)
count, bins, ignored = plt.hist(s, 14, normed=True)
#plt.show()

def nextTime(rateParameter):
    return -math.log(1.0 - random.random()) / rateParameter

def nextTime_process(times, index, rateParameter):
    times[index] = -math.log(1.0 - random.random()) / rateParameter[index]

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
order_cancellation_rate = 0.2 #units of 1/time(ms) - 1 cancelled every 10 ms on average
#now make poisson processes for each of the 5 processes -
#Market Order Buy, Market Order Sell, Limit Order Buy, Limit Order Sell, Order Cancel
#they will each generate the next time step, and then for the earliest time, if it is a
#limit order, project it onto the (log) price dimension, spaced at every dp intervals
begin_time = time.time() #this is the beginning of the trade simulation process
#Limit orders - poisson process over time, then poisson process over price, decide on cancellation
#time through poisson process over time
#Market Orders - poisson process over time
id = 0 #the last market/limit order id processed
market_order_buy_ids_queue = () #list of market orders buys - will be in a queue format
market_order_sell_ids_queue = () #list of market orders sells - will be in a queue format
limit_order_buy_ids_queue = () #list of limt order buys - will be in a queue format
limit_order_sell_ids_queue = () #list of limt order sells - will be in a queue format
#print(nextTime(order_cancellation_rate))
num_possible_orders = 4
rate_parameters_per_process = [None] * num_possible_orders
rate_parameters_per_process[0] = market_order_rate_buy #0 - market order buy
rate_parameters_per_process[1] = market_order_rate_sell #1 - market order sell
rate_parameters_per_process[2] = limit_order_rate_buy #2 - limit order buy
rate_parameters_per_process[3] = limit_order_rate_sell #3 - limit order sell
#first of all, initialize the order book to a reasonable approximation of the steady-state distribution
#meaning, place limit buy and limit sell orders after choosing the midpoint of the spread
#they will probably change once they equilibriate
lowest_ask = 104.00
highest_bid = 102.00
spread = lowest_ask - highest_bid
mid_spread = (lowest_ask + highest_bid) / 2
#print("Spread = %f, Midpoint = %f" % (spread, mid_spread))
#now, fill up the order book
#bids will be placed from lowest ask to -infinity and asks will be placed from highest bid to +infinity
#print(begin_time)
end_time = begin_time + 20 #build initial LOB for 20 seconds
num_possible_orders_i = 2
k = 0
while(time.time() <= end_time):
    threads = [None] * num_possible_orders_i
    times = [None] * num_possible_orders_i
    for i in range(num_possible_orders_i):
        threads[i] = threading.Thread(target=nextTime_process, args=(times, i, rate_parameters_per_process[2:4]))
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    min_time = min(times)

    print("Iteration %d, Limit Order Buy Time = %f, Limit Order Sell Time = %f, Minimum Time = %f, "
          "Index of minimum time = %d"
          % (k + 1, times[0], times[1], min_time, times.index(min_time)))
    k = k + 1

j = 0
while(j <= 10):
    #now, spawn 4 threads each for market buy, market sell, limit buy, limit sell
    #see which one has the lowest next time
    threads = [None] * num_possible_orders
    times = [None] * num_possible_orders
    for i in range(num_possible_orders):
        threads[i] = threading.Thread(target=nextTime_process, args=(times, i, rate_parameters_per_process))
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    min_time = min(times)

    print("Iteration %d, Market Order Buy Time = %f, Market Order Sell Time = %f, Limit Order Buy Time = %f, "
          "Limit Order Sell Time = %f, Minimum Time = %f, Index of minimum time = %d"
          % (j + 1, times[0], times[1], times[2], times[3], min_time, times.index(min_time)))


    j = j + 1










