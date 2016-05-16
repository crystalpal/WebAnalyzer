# -*- coding: utf-8 -*-
"""
dataStructures.py

@author: Joren & Vincent

"""
import time as tm
import pandas as pd
from utilities import gettimeofday
from itertools import chain


class Action(object):
    """ This datastructure is a wrapper for events or action; mainly click
    """
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
        if timeformat is None:  # If no timeformat given, take current time
           self.timestamp = round(tm.time(),1)
        else:
            self.timestamp = tm.mktime(timeformat)
        self.color = color

    def __str__(self):
        return ("Action: "+str(self.action)
                +", Link: "+str(self.link)
                +", Previous: "+str(self.previous))

    def update_link(self, new_link, domain):
        self.link = new_link
        self.domain = domain


class Domain(object):
    dom = ""
    urls = pd.Series()
    trail = 0

    def __init__(self, domain):
        self.dom = domain
        self.urls = pd.Series()

    def __str__(self):
        return (self.dom)
        
    def addurl(self, url):
        if url not in self.urls.keys():
            self.urls.set_value(url, 1)
        else:
            self.urls[url] += 1
        self.urls.sort_values(ascending=False)


class CircularList():
    items = []

    def __init__(self):
        self.items = [[] for x in range(60*24)]

    def add(self, domain, timestamp):
        """ Add a domain to a timeslot within a day """
        x = gettimeofday(timestamp)
        if len(self.items[x]) == 0:  # If empty, initialize cell
            self.items[x] = []
        self.items[x].append(domain)

    def getrangearound(self, timestamp, minutes):
        """ Suggest domains at the given timestamp within a given deviation
        based on their occurence count """
        start = gettimeofday(timestamp - minutes*60)
        end = gettimeofday(timestamp + minutes*60)
        if start > end:  # start < 0 or end > 60*60*24:
            rangechain = chain(range(0,end), range(start, 60*24))
        else:
            rangechain = range(start,end)
        alldomains = pd.Series()
        for i in rangechain:
            for dom in self.items[i]:
                val = 1
                if dom in alldomains.keys():
                    val = alldomains.get_value(dom) + val
                alldomains.set_value(dom, val)
        # Sort all domains based on their occurence count
        alldomains = alldomains.sort_values(ascending=False)
        return alldomains

            
