import math
import numpy as np
from scipy.stats import rv_discrete
import threading
import time
import logging
import random
import matplotlib.pyplot as plt
from limit_order import *
#import joystick as jk
from LOB import *

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
curr_time = time.time()
curr_time_from_beg = curr_time - begin_time
lob = LimitOrderBook()
id = 0
while(curr_time <= end_time):
#while(k < 10):
    curr_time_from_beg = curr_time - begin_time
    threads = [None] * num_possible_orders_i
    times = [None] * num_possible_orders_i
    for i in range(num_possible_orders_i):
        threads[i] = threading.Thread(target=nextTime_process, args=(times, i, rate_parameters_per_process[2:4]))
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    min_time = min(times)

    '''print("Iteration %d, Limit Order Buy Time = %f, Limit Order Sell Time = %f, Minimum Time = %f, "
          "Index of minimum time = %d"
          % (k + 1, times[0], times[1], min_time, times.index(min_time)))'''
    #now, pick a price based on whether or not it was buy or sell
    prices_range = np.ones(1) #only to initialize
    probability = np.ones(1) #only to initialize - uniform distribution
    buy_or_sell = times.index(min_time)
    cancel_time = nextTime(order_cancellation_rate)
    buy_sell = 1 #just an argument to pass to LimitOrder object (-1 is buy, +1 is sell)
    if (buy_or_sell == 0): #buy
        prices_range = np.arange(highest_bid - 5, highest_bid + dp, dp)
        prob = (float) (1.0 / len(prices_range))
        probability = np.full(len(prices_range), prob)
        '''print("Highest Bid before = %f" % highest_bid)
        highest_bid = max(prices_range)
        print("Highest Bid now = %f" % highest_bid)
        print("Lowest Ask now = %f" % lowest_ask)'''
        #lo = LimitOrder(k + 1, -1, time.time() - begin_time, cancel_time, orders)
        buy_sell = -1

    else: #sell
        prices_range = np.arange(lowest_ask, lowest_ask + 5 + dp, dp)
        prob = (float) (1.0 / len(prices_range))
        probability = np.full(len(prices_range), prob)

        '''print("Lowest Ask before = %f" % lowest_ask)
        lowest_ask = max(prices_range)
        print("Lowest Ask now = %f" % lowest_ask)
        print("Highest Bid now = %f" % highest_bid)'''
    '''print(prices_range)
    print(probability)'''
    distrib = rv_discrete(values=(prices_range, probability))
    price_picked = distrib.rvs(size=1)
    '''print(price_picked)
    print(price_picked[0])'''
    lo = LimitOrder(id + 1, buy_sell, price_picked[0], curr_time + min_time - begin_time, cancel_time, orders, lob) #make a limit order object
    lob.add_limit_order(lo) #add the limit order to the limit order book
    #print("Price Picked = %f" % price_picked)
    '''if (buy_or_sell == 0): #buy
        #check if the highest bid has changed
        if (price_picked > highest_bid): #if spread has changed due to highest bid changing
            print("Highest bid has changed. Highest bid before = %f, Highest bid now = %f"
                  % (highest_bid, price_picked))
            highest_bid = price_picked
            spread_new = lowest_ask - highest_bid
            print("Spread will also change. Spread before = %f, Spread now = %f"
                  %(spread, spread_new))
            spread = spread_new
        else: #spread remains the same
            print("Spread and Highest Bid remain the same. Spread = %f, Highest Bid = %f"
                  % (spread, highest_bid))
    else: #sell
        if (price_picked < lowest_ask):
            print("Lowest Ask has changed. Lowest Ask before = %f, Lowest Ask now = %f"
                  % (lowest_ask, price_picked))
            lowest_ask = price_picked
            spread_new = lowest_ask - highest_bid
            print("Spread will also change. Spread before = %f, Spread now = %f"
                  % (spread, spread_new))
            spread = spread_new
        else:  # spread remains the same
            print("Spread and Lowest Ask remain the same. Spread = %f, Lowest Ask = %f"
                  % (spread, lowest_ask))'''
    '''print("Price Picked = %f" % price_picked)
    print("Spread before = %f" % spread)
    spread = lowest_ask - highest_bid
    print("Spread now = %f" % spread)'''
    curr_time = time.time()
    k = k + 1
    id = id + 1 #for the next limit order's id

print("At the end of steady state. Highest Bid = %f, Lowest Ask = %f, Spread = %f"
      % (highest_bid, lowest_ask, spread))
lob.show_lob() #to see the contents



def generate_next_order(time_started, next_time_to_start, idx, ret_lst):
    while (time.time() - time_started < next_time_to_start):
        i = 0
    lowest_ask = 0.0
    highest_bid = 0.0
    if (idx == 0): #a market buy order was generated, then delete sell side
        '''print("Previous highest bid = %f, Previous lowest ask = %f, Previous spread = %f"
              %(highest_bid, lowest_ask, spread))'''
        lob.del_limit_sell()
        #lowest_ask = lob.limit_sells[0][0] #lowest ask has changed
        lowest_ask = lob.get_lowest_ask()
        highest_bid = lob.get_highest_bid()
        spread = lowest_ask - highest_bid
        '''print("Current highest bid = %f, Current lowest ask = %f, Current spread = %f"
              % (highest_bid, lowest_ask, spread))'''
    elif (idx == 1): #a market sell order was generated, then delete buy side
        '''print("Previous highest bid = %f, Previous lowest ask = %f, Previous spread = %f"
              % (highest_bid, lowest_ask, spread))'''
        lob.del_limit_buy()
        #highest_bid = lob.limit_buys[0][0] #highest bid has changed
        lowest_ask = lob.get_lowest_ask()
        highest_bid = lob.get_highest_bid()
        spread = lowest_ask - highest_bid
        '''print("Current highest bid = %f, Current lowest ask = %f, Current spread = %f"
          % (highest_bid, lowest_ask, spread))'''



    #now, if it is a limit order, add this to the limit order book
    elif (idx == 2): #limit buy
        lowest_ask = lob.get_lowest_ask() #the lowest ask currently
        prices_range = np.arange(lowest_ask - 5, lowest_ask + dp, dp) #the price range
        prob = (float)(1.0 / len(prices_range))
        probability = np.full(len(prices_range), prob)
        distrib = rv_discrete(values=(prices_range, probability))
        price_picked = distrib.rvs(size=1) #pick a price from the range
        lo = LimitOrder(id + 1, -1, price_picked[0], curr_time + min_time - begin_time,
                        cancel_time, orders,
                        lob)  # make a limit order object
        lob.add_limit_order(lo)  # add the limit order to the limit order book

        #spawn a new thread to check if this limit order has reached cancellation time
        t = threading.Thread(target=poke_per_limitorder, args=(lo, curr_time + min_time))
        t.start()

        #check to see if the highest bid has changed due to this buy limit order
        highest_bid = lob.get_highest_bid()


    else: #limit sell
        highest_bid = lob.get_highest_bid() #the highest bid currently
        prices_range = np.arange(highest_bid, highest_bid + 5 + dp, dp) #the price range
        prob = (float)(1.0 / len(prices_range))
        probability = np.full(len(prices_range), prob)
        distrib = rv_discrete(values=(prices_range, probability))
        price_picked = distrib.rvs(size=1) #pick a price from the range
        lo = LimitOrder(id + 1, 1, price_picked[0], curr_time + min_time - begin_time,
                        cancel_time, orders,
                        lob)  # make a limit order object
        lob.add_limit_order(lo)  # add the limit order to the limit order book

        # spawn a new thread to check if this limit order has reached cancellation time
        t = threading.Thread(target=poke_per_limitorder, args=(lo, curr_time + min_time))
        t.start()

        # check to see if the lowest ask has changed due to this ask limit order
        lowest_ask = lob.get_lowest_ask()

    #ret_lst = ()
    ret_lst.append(highest_bid)
    ret_lst.append(lowest_ask)



j = 0
curr_time = time.time()



while(True):
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
    idx = times.index(min_time)

    print("Iteration %d, Market Order Buy Time = %f, Market Order Sell Time = %f, Limit Order Buy Time = %f, "
          "Limit Order Sell Time = %f, Minimum Time = %f, Index of minimum time = %d"
          % (j + 1, times[0], times[1], times[2], times[3], min_time, idx))

    ret_lst = list()
    th = threading.Thread(target=generate_next_order, args=(curr_time, min_time, idx, ret_lst))
    th.start()

    th.join()

    # #now if it is a market order, then access the limit order book object, and extract the opposite
    # #side's market offer, and then change the highest bid and lowest ask, and thereby the spread value
    # #no synchronization needed here
    # if (idx == 0): #a market buy order was generated, then delete sell side
    #     '''print("Previous highest bid = %f, Previous lowest ask = %f, Previous spread = %f"
    #           %(highest_bid, lowest_ask, spread))'''
    #     lob.del_limit_sell()
    #     #lowest_ask = lob.limit_sells[0][0] #lowest ask has changed
    #     lowest_ask = lob.get_lowest_ask()
    #     highest_bid = lob.get_highest_bid()
    #     spread = lowest_ask - highest_bid
    #     '''print("Current highest bid = %f, Current lowest ask = %f, Current spread = %f"
    #           % (highest_bid, lowest_ask, spread))'''
    # elif (idx == 1): #a market sell order was generated, then delete buy side
    #     '''print("Previous highest bid = %f, Previous lowest ask = %f, Previous spread = %f"
    #           % (highest_bid, lowest_ask, spread))'''
    #     lob.del_limit_buy()
    #     #highest_bid = lob.limit_buys[0][0] #highest bid has changed
    #     lowest_ask = lob.get_lowest_ask()
    #     highest_bid = lob.get_highest_bid()
    #     spread = lowest_ask - highest_bid
    #     '''print("Current highest bid = %f, Current lowest ask = %f, Current spread = %f"
    #       % (highest_bid, lowest_ask, spread))'''
    #
    #
    #
    # #now, if it is a limit order, add this to the limit order book
    # elif (idx == 2): #limit buy
    #     lowest_ask = lob.get_lowest_ask() #the lowest ask currently
    #     prices_range = np.arange(lowest_ask - 5, lowest_ask + dp, dp) #the price range
    #     prob = (float)(1.0 / len(prices_range))
    #     probability = np.full(len(prices_range), prob)
    #     distrib = rv_discrete(values=(prices_range, probability))
    #     price_picked = distrib.rvs(size=1) #pick a price from the range
    #     lo = LimitOrder(id + 1, -1, price_picked[0], curr_time + min_time - begin_time,
    #                     cancel_time, orders,
    #                     lob)  # make a limit order object
    #     lob.add_limit_order(lo)  # add the limit order to the limit order book
    #
    #     #spawn a new thread to check if this limit order has reached cancellation time
    #     t = threading.Thread(target=poke_per_limitorder, args=(lo, curr_time + min_time))
    #     t.start()
    #
    #     #check to see if the highest bid has changed due to this buy limit order
    #     highest_bid = lob.get_highest_bid()
    #
    #
    # else: #limit sell
    #     highest_bid = lob.get_highest_bid() #the highest bid currently
    #     prices_range = np.arange(highest_bid, highest_bid + 5 + dp, dp) #the price range
    #     prob = (float)(1.0 / len(prices_range))
    #     probability = np.full(len(prices_range), prob)
    #     distrib = rv_discrete(values=(prices_range, probability))
    #     price_picked = distrib.rvs(size=1) #pick a price from the range
    #     lo = LimitOrder(id + 1, 1, price_picked[0], curr_time + min_time - begin_time,
    #                     cancel_time, orders,
    #                     lob)  # make a limit order object
    #     lob.add_limit_order(lo)  # add the limit order to the limit order book
    #
    #     # spawn a new thread to check if this limit order has reached cancellation time
    #     t = threading.Thread(target=poke_per_limitorder, args=(lo, curr_time + min_time))
    #     t.start()
    #
    #     # check to see if the lowest ask has changed due to this ask limit order
    #     lowest_ask = lob.get_lowest_ask()

    #now, that orders have been generated, we have to service limit order matchings
    highest_bid = ret_lst[0]
    lowest_ask = ret_lst[1]
    if (lowest_ask == highest_bid or lowest_ask < highest_bid): #delete both lowest ask and highest bid indicating they have been fulfilled
        print("Matched limit buy with limit sell...")
        lob.del_limit_buy()
        lob.del_limit_sell()
    #otherwise, no trade took place
    '''else:
        print("No trading took place...")'''


    curr_time = time.time()
    j = j + 1










