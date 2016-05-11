# -*- coding: utf-8 -*-
"""
utilities.py

@author: Joren & Vincent

"""
import time as tm
import pandas as pd


def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        content = content.replace(", ", ",")
        content = content.replace('"', "")
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def gettimeofday(timestamp):
    time = tm.gmtime(timestamp)
    hours = (time.tm_hour)*60*60
    minutes = time.tm_min * 60
    seconds = time.tm_sec
    return hours + minutes + seconds


def addtopath(paths, n, score):
    if n in paths.keys():
        paths[n] += score
    else:
        paths[n] = score


def domainsuggestions(paths, urls):
    domainsuggestions = pd.Series()
    for index in paths.keys():
        if urls[index].domain.dom in domainsuggestions:
            domainsuggestions[urls[index].domain.dom].append(index)
        else:
            domainsuggestions[urls[index].domain.dom] = [index]
    print("Domainsuggestions:")
    print(domainsuggestions)
    return domainsuggestions


def combinesuggestionstime(timeproposals, domainsuggestions):
    suggestions = []
    fill = 4 - len(timeproposals)
    print(fill)
    for domain in timeproposals.keys()[:2]:
        if domain in domainsuggestions.keys():
            for d in domainsuggestions[domain][:2]:
                suggestions.append(d)
    for domain in timeproposals.keys()[2:4]:
        if domain in domainsuggestions.keys():
            for d in domainsuggestions[domain][0]:
                suggestions.append(d)
    if fill > 0:
        domains = [x for x in domainsuggestions.keys() if x not in timeproposals.keys()[:4]]
        for domain in domains[:fill]:
            for d in domainsuggestions[domain][:1]:
                suggestions.append(d)
    return suggestions


def combinesuggestions(current, timeproposals, domainsuggestions, urls, amount):
    suggestions = []
    for domain in domainsuggestions.keys()[:1]:
        for d in domainsuggestions[domain][:2]:
            if d not in suggestions:
                suggestions.append(d)
    for domain in domainsuggestions.keys()[1:3]:
        for d in domainsuggestions[domain][:1]:
            if d not in suggestions:
                suggestions.append(d)
    domains = [x for x in timeproposals.keys() if x not in suggestions]
    for domain in domains:
        if domain in domainsuggestions.keys():
            for d in domainsuggestions[domain][:1]:
                if d not in suggestions:
                    suggestions.append(d)
                    break 
    length = 0
    cur = len(suggestions)
    if amount > cur:               
        if amount - cur < len(current.domain.urls):
            length = amount - len(suggestions)
        else: 
            length = len(current.domain.urls)
    print("lennie")
    print(length)
    if len(suggestions) < amount:
        for i in range(0, length):
            suggestions.append(current.domain.urls.keys()[i])
    '''
    if len(suggestions) < amount:
        for domain in domainsuggestions.keys():
            for d in domainsuggestions[domain][:1]:
                if d not in suggestions:
                    suggestions.append(d)
                    if len(suggestions) == amount:
                        return suggestions
    '''
    return suggestions


def combinetimeproposals(dayproposals, weekproposals):
    timeproposals = pd.Series()
    for daydomain in dayproposals.keys():
        if daydomain in weekproposals.keys():
            # divide by 7 & 8, reducing the influence a single outburst has
            count = dayproposals[daydomain]/7 + weekproposals[daydomain]/8
            timeproposals[daydomain] = count
        else:
            timeproposals[daydomain] = dayproposals[daydomain]
    # calculate belief of timeproposals
    if(len(timeproposals) > 0):
        avgscore = float(sum(timeproposals.values)/len(timeproposals.values)) - 1/len(timeproposals.values)
    else:
        avgscore = 0
    timeproposals = pd.Series({proposal:timeproposals[proposal] for proposal in timeproposals.keys() if timeproposals[proposal] > avgscore})
    print("timeproposals")
    print(timeproposals)
    return timeproposals.sort_values(ascending=False)
