# -*- coding: utf-8 -*-
"""
utilities.py

@author: Joren & Vincent

"""
import time as tm
import pandas as pd
import math as m

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


def combine_suggestions(current, timeproposals, domainsug, urls, domains, amount):    
    """ Combine all suggestions to one list of length amount that can be
        returned """
    """
    print("Domainsuggestions:")
    print(domainsug)
    print("Timesuggestions:")
    print(timeproposals)
    """

    suggestions = []
    firstsuggestions = m.floor(amount/10*8)
      
    """ add for the first X domain the top 1 links """
    for domain in domainsug.keys()[0:firstsuggestions]:
        for d in domainsug[domain][:1]:
            if d not in suggestions:
                suggestions.append(d)
            else:
                firstsuggestions += 1
                
    """ add for the first two timedomains the top 1 links if in domains and
    timedomains not already in suggestions """
    timesuggestions = []
    nextsuggestions = amount - len(suggestions)
    for domain in timeproposals.keys()[0:nextsuggestions]:
        if domain in domainsug.keys():
            for proposal in domainsug[domain][:1]:
                if not proposal in suggestions:
                    suggestions.append(proposal)
                    timesuggestions.append(suggestions[-1])
                else:
                    nextsuggestions += 1
    
    """ if no timesuggestions could be found for the domains, use the top
    domains instead """
    nextsuggestions = amount - len(suggestions)
    if nextsuggestions > 0:
        for domain in timeproposals.keys()[len(timesuggestions):nextsuggestions]:
            for proposal in domains[domain].urls.keys()[:1]:
                if not proposal in suggestions: 
                    suggestions.append(proposal)
                else:
                    nextsuggestions += 1
                    
    """ if the amount of suggestions is not met, start adding urls
    of the current domain using mle """
    softmle = amount - len(suggestions)  
    if softmle > 0:     
        for url in current.domain.urls.keys()[0:softmle]:
            if not url in suggestions:
                suggestions.append(url)
            else:
                softmle += 1     
        
    """ if the amount of suggestions is not met, start adding urls
    from the most visted domains usings mle """
    hardmle = amount - len(suggestions)
    if hardmle > 0: 
        for domain in list(domains.keys())[0:hardmle]:
            for url in domains[domain].urls[:1]:
                if not url in suggestions:
                    suggestions.append(url)
                else:
                    hardmle += 1
  
    return suggestions


def combine_timeproposals(dayproposals, weekproposals):
    """ Returns a sorted pandas.Series() of the combined weight where
        weekproposals get a bonusweight if they appear in the dayproposals"""
    if dayproposals.size == 0:
        if weekproposals.size == 0:
            return dayproposals
        return weekproposals
    if weekproposals.size == 0:
            return dayproposals
            
    extrabonus = weekproposals.mean()
    max_week = weekproposals[0]
    max_day = dayproposals[0]
    tps = pd.Series()  # timeproposals
    for daydomain in weekproposals.keys():
        if daydomain in dayproposals.keys():
            # Normalise both values, sum them so the day value gets a clear
            # advantage (less links means higher normalised values)
            # multiply by normalisation again and add extra bonus
            daycount = dayproposals[daydomain]/max_day
            weekcount = weekproposals[daydomain]/max_week
            tps[daydomain] = (daycount + weekcount) * max_week + extrabonus
        else:
            tps[daydomain] = weekproposals[daydomain]
    # calculate belief of timeproposals
    if(tps.size > 0):
        prop_amount = len(tps.values)
        avgscore = float(sum(tps.values)/prop_amount) - 1/prop_amount
    else:
        avgscore = 0
    tps = pd.Series({p: tps[p] for p in tps.keys() if tps[p] > avgscore})
    return tps.sort_values(ascending=False)
