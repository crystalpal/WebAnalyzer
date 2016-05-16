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
    """" Returns the time of day in seconds"""
    time = tm.gmtime(timestamp)
    hours = (time.tm_hour)*60
    minutes = time.tm_min
    return hours + minutes
    

def parse_timestamp(timestamp, seconds=True):
    """ Parse timestamp - everything except for miliseconds after the dot """
    parsed = tm.strptime(timestamp.split('.')[0], "%Y-%m-%dT%H:%M:%S")
    if not seconds: 
        return parsed
    return tm.mktime(parsed)


def addtopath(paths, n, score):
    if n in paths.keys():
        paths[n] += score
    else:
        paths[n] = score


def domain_suggestions(paths, urls):
    domainsuggestions = pd.Series()
    for index in paths.keys():
        if urls[index].domain.dom in domainsuggestions:
            domainsuggestions[urls[index].domain.dom].append(index)
        else:
            domainsuggestions[urls[index].domain.dom] = [index]
    return domainsuggestions


def combine_suggestionstime(timeproposals, doms):
    suggestions = []
    fill = 4 - len(timeproposals)
    for domain in timeproposals.keys()[:2]:
        if domain in doms.keys():
            for d in doms[domain][:2]:
                suggestions.append(d)
    for domain in timeproposals.keys()[2:4]:
        if domain in doms.keys():
            for d in doms[domain][0]:
                suggestions.append(d)
    if fill > 0:
        domains = [x for x in doms.keys() if x not in timeproposals.keys()[:4]]
        for domain in domains[:fill]:
            for d in doms[domain][:1]:
                suggestions.append(d)
    return suggestions


def combine_suggestions(current, timeproposals, domainsug, urls, amount):    
    """    
    print("Domainsuggestions:")
    print(domainsug)
    print("Timesuggestions:")
    print(timeproposals)
    """
    suggestions = []
    
      
    for domain in domainsug.keys()[1:3]:
        for d in domainsug[domain][:1]:
            if d not in suggestions:
                suggestions.append(d)
    
    for proposal in timeproposals.keys()[1:3]:
        if proposal in domainsug.keys():
            suggestions.append(domainsug[proposal][:1])
  
    domains = [x for x in timeproposals.keys() if x not in suggestions]
    counter = 0
    for domain in domains:
        if domain in domainsug.keys():
            for d in domainsug[domain][:1]:
                if d not in suggestions:
                    suggestions.append(d)
                    counter += 1
                    if counter == 2:
                        break
    length = 0
    cur = len(suggestions)
    if amount > cur:
        if amount - cur < len(current.domain.urls):
            length = amount - len(suggestions)
        else:
            length = len(current.domain.urls)
    if len(suggestions) < amount:
        for i in range(0, length):
            suggestions.append(current.domain.urls.keys()[i])
    
    if len(suggestions) < amount:
        for domain in domainsug.keys():
            for d in domainsug[domain][:1]:
                if d not in suggestions:
                    suggestions.append(d)
                    if len(suggestions) == amount:
                        return suggestions
    return suggestions


def combine_timeproposals(dayproposals, weekproposals):
    tps = pd.Series()  # timeproposals
    for daydomain in dayproposals.keys():
        if daydomain in weekproposals.keys():
            # divide by 7 & 8, reducing the influence a single outburst has
            count = dayproposals[daydomain] + weekproposals[daydomain]
            tps[daydomain] = count
        else:
            tps[daydomain] = dayproposals[daydomain]
    # calculate belief of timeproposals
    if(len(tps) > 0):
        prop_amount = len(tps.values)
        avgscore = float(sum(tps.values)/prop_amount) - 1/prop_amount
    else:
        avgscore = 0
    tps = pd.Series({p: tps[p] for p in tps.keys() if tps[p] > avgscore})
    return tps.sort_values(ascending=False)
