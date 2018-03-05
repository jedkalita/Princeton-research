import os
import math
import sys
import time
from limit_order import *
import numpy as np

class LimitOrderBook:
    def __init__(self):
        self.limit_buys = np.ones(1, 3) #will store the limit buys  - will be appended - (price, time, id)
        self.limit_sells = np.ones(1, 3) #will store the limit sells  - will be appended - (price, time, id)
        self.limit_buy_count = 0
        self.limit_sell_count = 0

    def add_limit_order(self, lo):
        if lo.id == -1: #a buy order
            newrow = [lo.price, lo.time_began, lo.id]
            self.limit_buys = np.append(self.limit_buys, [newrow], axis = 0)
            self.limit_buy_count = self.limit_buy_count + 1
            if self.limit_buy_count == 1: #if it is the first limit order buy order
                self.limit_buys = np.delete(self.limit_buys, 0, 0)  # delete the ones row created just to initialize
            #now, arrange the buy orders in decreasing order of price, and in increasing order of times
            self.limit_buys = self.limit_buys[np.lexsort((self.limit_buys[:, 1], -self.limit_buys[:, 0]))]
        else: #a sell order
            newrow = [lo.price, lo.time_began, lo.id]
            self.limit_sells = np.append(self.limit_sells, [newrow], axis=0)
            self.limit_sell_count = self.limit_buy_count + 1
            if self.limit_sell_count == 1:  # if it is the first limit order buy order
                self.limit_sells = np.delete(self.limit_sells, 0, 0)  # delete the ones row created just to initialize
            # now, arrange the buy orders in increasing order of price, and in increasing order of times
            self.limit_sells = self.limit_buys[np.lexsort((self.limit_sells[:, 1], self.limit_sells[:, 0]))]


