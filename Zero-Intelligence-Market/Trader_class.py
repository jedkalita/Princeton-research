import os
import math
import sys
import time
from LOB import *


class Trader:
    def __init__(self, lob):
        self.lob = lob

    def generate_limit_order(self, neg_id, begin_time):
        lo = LimitOrder(neg_id, 1, 104, time.time() - begin_time, 10, 1, lob)
        return lo
