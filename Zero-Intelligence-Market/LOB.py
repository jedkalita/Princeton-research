import os
import math
import sys
import time
from limit_order import *
import numpy as np
from scipy.stats import rv_discrete
import random
import threading

class LimitOrderBook:
    def __init__(self):
        self.limit_buys = np.ones((1, 3)) #will store the limit buys  - will be appended - (price, time, id)
        self.limit_sells = np.ones((1, 3)) #will store the limit sells  - will be appended - (price, time, id)
        self.limit_buy_count = 0
        self.limit_sell_count = 0

    def add_limit_order(self, lo):
        if lo.buy_or_sell == -1: #a buy order
            newrow = [lo.price, lo.time_began, int(lo.id)]
            #print(newrow)
            self.limit_buys = np.append(self.limit_buys, [newrow], axis = 0)
            self.limit_buy_count = self.limit_buy_count + 1
            if self.limit_buy_count == 1: #if it is the first limit order buy order
                #print("Deleting...")
                self.limit_buys = np.delete(self.limit_buys, 0, 0)  # delete the ones row created just to initialize

            #now, arrange the buy orders in decreasing order of price, and in increasing order of times
            self.limit_buys = self.limit_buys[np.lexsort((self.limit_buys[:, 1], -self.limit_buys[:, 0]))]
            '''print("Added a limit buy order. Displaying the limit buy orders...")
            print(self.limit_buys)'''
        else: #a sell order
            newrow = [lo.price, lo.time_began, int(lo.id)]
            #print(newrow)
            self.limit_sells = np.append(self.limit_sells, [newrow], axis = 0)
            self.limit_sell_count = self.limit_sell_count + 1
            if self.limit_sell_count == 1:  # if it is the first limit order buy order
                #print("Deleting...")
                self.limit_sells = np.delete(self.limit_sells, 0, 0)  # delete the ones row created just to initialize

            # now, arrange the buy orders in increasing order of price, and in increasing order of times
            self.limit_sells = self.limit_sells[np.lexsort((self.limit_sells[:, 1], self.limit_sells[:, 0]))]
            '''print("Added a limit sell order. Displaying the limit sell orders...")
            print(self.limit_sells)'''

    def del_limit_buy(self): #when a market sell order is generated, then remove the highest bid
        #print(self.limit_buys.shape)
        self.limit_buys = np.delete(self.limit_buys, 0, 0)
        #print(self.limit_buys.shape)
        # now, arrange the buy orders in decreasing order of price, and in increasing order of times
        #self.limit_buys = self.limit_buys[np.lexsort((self.limit_buys[:, 1], -self.limit_buys[:, 0]))]
        self.limit_buy_count = self.limit_buy_count - 1
        '''print("Just deleted a limit buy order. Displaying the limit buys now...")
        print(self.limit_buys)'''

    def del_limit_sell(self): #when a market buy order is generated, then remove the lowest ask
        #print(self.limit_sells.shape)
        self.limit_sells = np.delete(self.limit_sells, 0, 0)
        #print(self.limit_sells.shape)
        # now, arrange the sell orders in increasing order of price, and in increasing order of times
        #self.limit_sell = self.limit_buys[np.lexsort((self.limit_sell[:, 1], -self.limit_sell[:, 0]))]
        self.limit_sell_count = self.limit_sell_count - 1
        '''print("Just deleted a limit sell order. Displaying the limit sells now...")
        print(self.limit_sells)'''

    def show_lob(self): #show the characteristics of the limit order book - by definition will be showing depth
        print("Limit Buy Orders.....")
        print(self.limit_buys)
        print("Limit Sell Orders.....")
        print(self.limit_sells)
        print("Total buy orders = %d, Total sell orders = %d" % (self.limit_buy_count, self.limit_sell_count))

def poke_per_limitorder(lo, begin_time):
    lo.poke(begin_time)


if __name__ == "__main__":
    k = 0
    begin_time = time.time()
    vals = np.arange(-1, 1 + 0.1, 2)
    prob = (float) (1.0 / len(vals))
    probability = np.full(len(vals), prob)
    lob = LimitOrderBook()
    while (k < 10):
        distrib = rv_discrete(values=(vals, probability))
        picked = distrib.rvs(size=1)
        print("Picked = %d" % picked)
        if (picked == -1): #a buy
            print("Trying to add a buy order")
            lo = LimitOrder(k + 1, int(picked), 102.25 + random.uniform(-3.0, 4.5),
                            time.time() - begin_time, 4.56 + random.uniform(-2.0, 10.9), 3, lob)
            lob.add_limit_order(lo)
        else: #a sell
            print("Trying to add a sell order")
            lo = LimitOrder(k + 1, int(picked), 104.5 + random.uniform(-3.0, 4.5), time.time() - begin_time,
                            4.56 + random.uniform(-2.0, 10.9), 3, lob)
            lob.add_limit_order(lo)

        t = threading.Thread(target=poke_per_limitorder, args=(lo, begin_time))
        t.start()

        k = k + 1

    '''distrib = rv_discrete(values=(vals, probability))
    picked = distrib.rvs(size=1)
    print("Picked = %d" % picked)
    if (picked == -1):  # a buy
        print("Trying to add a buy order")
        lo = LimitOrder(k + 1, int(picked), 102.25 + random.uniform(-3.0, 4.5),
                        time.time() - begin_time, 4.56 + random.uniform(-2.0, 10.9), 3, lob)
        lob.add_limit_order(lo)
    else:  # a sell
        print("Trying to add a sell order")
        lo = LimitOrder(k + 1, int(picked), 104.5 + random.uniform(-3.0, 4.5), time.time() - begin_time,
                        4.56 + random.uniform(-2.0, 10.9), 3, lob)
        lob.add_limit_order(lo)
    t = threading.Thread(target=poke_per_limitorder, args=(lo, begin_time))
    t.start()'''

    lob.show_lob()
    '''lob.del_limit_buy()
    lob.del_limit_sell()
    lob.show_lob()'''




