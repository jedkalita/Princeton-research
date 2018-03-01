#!/bin/python3

import sys
import os


# Complete the function below.
def helper_Pangram(string):
    checker = list()
    for i in range(26):
        checker.append(0)
    base = ord('a')
    for l in string:
        if l == " ":
            continue
        checker[ord(l) - base] = 1
    for l in checker:
        if(l == 0):
            return 0
    return 1


def isPangram(strings):
    print('eeeee')
    length = len(strings)
    print(length)

if __name__ == "__main__":
    s = 'we promptly judged antique ivory buckles for the prizes'
    x = helper_Pangram(s)
    print(x)
    isPangram(s)
    a = ['a', 'b', 'c', 'd']
    a.pop(2)
    print(a)