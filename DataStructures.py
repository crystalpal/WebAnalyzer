# -*- coding: utf-8 -*-
"""
dataStructures.py

@author: Joren & Vincent

"""
import time as tm
import pandas as pd
from utilities import gettimeofday


class Action(object):
    action = ""
    domain = ""
    previous = ""
    link = ""
    timestamp = ""
    color = ""

    def __init__(self, action, domain, previous, link, timeformat, color):
        self.action = action
        self.domain = domain
        self.previous = previous
        self.link = link
        self.timestamp = tm.mktime(timeformat)
        self.color = color


class Domain(object):
    dom = ""
    urls = pd.Series()
    trail = 0

    def __init__(self, url):
        self.dom = url
        self.urls = pd.Series()


class CircularList():
    items = []

    def __init__(self):
        self.items = [[] for x in range(60*60*24)]

    def add(self, domain, timestamp):
        x = gettimeofday(timestamp)
        if len(self.items[x]) == 0:
            self.items[x] = []
            self.items[x].append(domain.dom)

    def getrange(self, timestamp, seconds):
        x = gettimeofday(timestamp)
        start = x - seconds
        end = x + seconds
        alldomains = pd.Series()
        if start < 0:
            start = 60*60*24 - start
            for i in range(x, end) + range(start, 60*60*24):
                for dom in self.items[i]:
                    if dom in alldomains.keys():
                        val = alldomains.get_value(dom) + 1
                        alldomains.set_value(dom, val)
                    else:
                        alldomains.set_value(dom, 1)
        elif end > 60*60*24:
            end = 0 + end
            for i in range(0, end) + range(start, x):
                for dom in self.items[i]:
                    if dom in alldomains.keys():
                        val = alldomains.get_value(dom) + 1
                        alldomains.set_value(dom, val)
                    else:
                        alldomains.set_value(dom, 1)
        else:
            for i in range(start, end):
                for dom in self.items[i]:
                    if dom in alldomains.keys():
                        val = alldomains.get_value(dom) + 1
                        alldomains.set_value(dom, val)
                    else:
                        alldomains.set_value(dom, 1)
        alldomains = alldomains.sort_values(ascending=False)
        return alldomains
