# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 14:41:32 2016

@author: Joren
"""
import csv
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time as tm
from scipy import cluster as cl
from matplotlib.colors import colorConverter
from collections import namedtuple
import copy
import calendar
import datetime
import pandas as pd
import os
import sys



file = 'C:/Users/Joren/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test.csv'
#file1 = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_16J.csv'
file2 = 'C:/Users/Joren/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_16J.csv'

colors = ["red", "blue", "yellow", "green", "purple", "white", "orange", "pink", "gray", "brown", "white", "silver", "gold", 
          "red", "blue", "yellow", "green", "purple", "white", "orange", "pink", "gray", "brown", "white", "silver", "gold"          
          "red", "blue", "yellow", "green", "purple", "white", "orange", "pink", "gray", "brown", "white", "silver", "gold"]  
 
class Action(object):
    action =""
    domain = ""
    link = ""
    timestamp = ""
    color = ""
    def __init__(self, action, domain, link, timeformat, color):
        self.action = action
        self.domain = domain
        self.link = link
        self.timestamp = tm.mktime(timeformat)
        self.color = color
    
  
class Domain(object):
    dom = ""
    urls = []
    trail = 0
    def __init__(self, url):
        self.dom = url
        self.urls = []
        
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
        alldomains = alldomains.sort_values(ascending = False)
        return alldomains
     
     
Edge = namedtuple("Edge", ["previous", "current"])

def gettimeofday(timestamp):
        time = tm.gmtime(timestamp)
        hours = (time.tm_hour)*60*60
        minutes = time.tm_min * 60
        seconds = time.tm_sec
        return hours + minutes + seconds   
        
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        content = content.replace(", ", ",")
        content = content.replace('"', "")
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') +  '\n' + content)

def parseClick(inputline):
    action = extractAction(inputline)
    insertAction(action)

def extractAction(inputline):
    inputline = inputline.replace("\"", "")
    inputline = inputline.replace(" ", "")
    row = inputline.split(',')
    timestamp = row[0]
    act = row[1]
    link = row [2]
    domain = link[link.index('//')+2:link.index('/', link.index('//'))]
    domain = link[link.index('//')+2:link.index('/', 12)]
    domain = domain.replace("www.", "")  
    domain = domain[:domain.rindex('.')]
    if "google" in link and "&" in link:
        link = link[0:link.index('&')]
    year = timestamp[:4]
    month = timestamp[5:-17]
    day = timestamp[8:-14]
    hour = timestamp[11:-11]
    minute = timestamp[14:-8]
    second = timestamp[17:-5]
    timeformat = tm.strptime(year +  " " + month + " " + " " + day + " " + hour + " " + minute + " " + second, "%Y %m %d %H %M %S")          
    return Action(act, domain, link, timeformat, colors[len(clicks)%9])

def insertAction(action):
    global lastnode
    global maxtime
    global domaintime
        #check how far the last unloaded page was in the past, and start a new trail if necessary
    if action.timestamp - lastnode.timestamp > 60*60: # in seconds = 1 hour
        trails.append([])
        intertrails.append((lastnode, action))  
                                  
    if action.action == "load":
        loads.append(action)
    if action.action == "click":
        clicks.append(action)       
        #check if the domain is already known in the system, if not initialize
        if not action.domain in domains.keys():
            domains[action.domain] = Domain(action.domain)
        domains[action.domain].urls.append(action)
        if len(clicks) > 1:
            previous = clicks[-2]
            urls[action.link] = action
            time = action.timestamp - previous.timestamp
            if time > maxtime:
                maxtime = time
            if not (previous.link, action.link) in F.edges():
                F.add_edge(previous.link, action.link, weight=0, time=0, trails = set())
            trails[-1].append((previous, action, time))
            F[previous.link][action.link][0]['weight'] += 1
            F[previous.link][action.link][0]['time'] = (F[previous.link][action.link][0]['time'] + time)/2
            F[previous.link][action.link][0]['trails'].add(len(trails))
            dom1 = domains[previous.domain]
            dom2 = domains[action.domain]
            weekday = tm.gmtime(action.timestamp).tm_wday
            if dom2.dom in weekdays[weekday].keys():
                val = weekdays[weekday].get_value(dom2.dom) + 1
                weekdays[weekday].set_value(dom2.dom, val)  
            else:
                weekdays[weekday].set_value(dom2.dom, 1)
            weekdays[weekday] = weekdays[weekday].sort_values(ascending = False)
            if not dom1.dom == dom2.dom:                    
                daytime.add(dom2, action.timestamp)
                G.add_edge(dom1, dom2)   
    lastnode = action
                
def dtraverse(G, source, current, maxi, trail, paths):
    if current == maxi:
        return
    for n in G.neighbors(source):
        if n.timestamp - source.timestamp < 20:
            dtraverse(G, n, current, maxi, trail, paths)
        else:
            score = F[source.link][n.link][0]['weight']
            trail[0].append(n)
            trail[1] += score
            paths.append(copy.deepcopy(trail))   
            current += 1
            dtraverse(G, n, current, maxi, trail, paths)

def depthtraverse(G, source, paths, current, maxdepth, lookaheadtime):    
    for n in G.neighbors(source):  
        score = G[source][n][0]['weight']
        if G[source][n][0]['time'] < lookaheadtime:
            if current == maxdepth:
                addtopath(paths, n, score)
                return
            depthtraverse(G, n, paths, (current+1), maxdepth, lookaheadtime)            
        else:
            addtopath(paths, n, score)

def breathtraverse(G, queue, paths, maxdepth, lookaheadtime):
    for idx in range(0, len(queue)):
        q = queue.pop(0)
        node, current = q[0], q[1]        
        for n in G.neighbors(node): 
            score = G[node][n][0]['weight']
            if current == maxdepth:
                addtopath(paths, n, score)
                return   
            if G[node][n][0]['time'] > lookaheadtime:
                addtopath(paths, n, score)
                queue.append((n, (current+1)))
            else:                        
                queue.append((n,current))
    breathtraverse(G, queue, paths, maxdepth, lookaheadtime)
    
            
def addtopath(paths, n, score):
    if n in paths.keys():
        paths[n] += score
    else:
        paths[n] = score
            
            
def proposeweektimes(proposed, amount):
    return weekdays[datetime.datetime.utcfromtimestamp(proposed.timestamp).weekday()][:amount]

def proposedaytimes(proposed, r, amount):
    return daytime.getrange(proposed.timestamp, r)[:amount]
        

#line_prepender(file2, 'time,action,link,other')  


f = open(file2)
#data = csv.reader(f, delimiter=',')
data = f

loads = []
clicks = [] # A list containing every click action
domains = {} # A dictionary mapping domain names on domain objects
urls = {} # A dictionnary mapping urls on action objects   
maxtime = 0 # The masimum time that is spent on a single url
domaintime = 0 # The maximum time that is spent in a domain // note, change both or add to trailtime 
trails = [0] # A list of trailid's containing their urls
trails[0] = []
intertrails = []
weekdays = {0:pd.Series(), 1:pd.Series(), 2:pd.Series(), 3:pd.Series(), 4:pd.Series(), 5:pd.Series(), 6:pd.Series()}
#daytime = {0:pd.Series(), 1:pd.Series(), 2:pd.Series(), 3:pd.Series(), 4:pd.Series(), 5:pd.Series(), 6:pd.Series(), 7:pd.Series()}
daytime = CircularList()
lastnode = Action(None, None, None, tm.strptime("1980 1 1 1 1 1", "%Y %m %d %H %M %S"), None)
'''
plt.figure(figsize=(10,10))
plt.axis('off') 
'''
F = nx.MultiDiGraph()
G = nx.MultiDiGraph()
p1 = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/allsets'
p2 = 'C:/Users/Joren//Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/u4'
path = p2
for fi in os.listdir(path):
    print(fi)
    iterrows = iter(open(path + "/"+fi))
    for row in iterrows:
        parseClick(str(row))
'''
#F.add_edges_from(edges)
nodevalues = [node.color for node in F.nodes()]
nodelabels = {clicks[node]:clicks[node].domain[clicks[node].domain.index('//')+2:] for node in range(0, len(F.nodes()))}
nodepos = nx.fruchterman_reingold_layout(F)
nodesizes = [(F.nodes()[index+1].timestamp - F.nodes()[index].timestamp)/maxtime*1000 for index in range(0, len(F.nodes())-1)]
nx.draw_networkx_nodes(F, nodepos, cmap=plt.get_cmap('jet'), node_color = nodevalues, node_size=nodesizes)
nx.draw_networkx_edges(F, nodepos, arrows=True)
nx.draw_networkx_labels(F, nodepos, nodelabels ,font_size=15)
plt.show() 
'''
'''
plt.figure(figsize=(10,10))
plt.axis('off') 
values = [colorConverter.to_rgba('y', alpha = index/(len(G.nodes()))) for index in range(0, len(G.nodes()))]
labels = {domains[node]:node for node in domains}
pos = nx.fruchterman_reingold_layout(G)
sizes = [len(node.urls)*1000 for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color = values, node_size=sizes)
nx.draw_networkx_edges(G, pos, arrows=True)
nx.draw_networkx_labels(G, pos, labels ,font_size=10)
'''
#plt.show()

def combinetimeproposals(dayproposals, weekproposals):
    timeproposals = pd.Series()
    for daydomain in dayproposals.keys():
        if daydomain in weekproposals.keys():
            #divide by 7 and 8, reducing the influence one single outburst has
            count = dayproposals[daydomain]/7 + weekproposals[daydomain]/8
            timeproposals[daydomain] = count
        else:
            timeproposals[daydomain] = dayproposals[daydomain]
    #calculate belief of timeproposals
    if(len(timeproposals) > 0):
        avgscore = float(sum(timeproposals.values)/len(timeproposals.values)) - 1/len(timeproposals.values)
    else:
        avgscore = 0
    timeproposals = pd.Series({proposal:timeproposals[proposal] for proposal in timeproposals.keys() if timeproposals[proposal] > avgscore})
    print("timeproposals")
    print(timeproposals)
    return timeproposals.sort_values(ascending = False)

def domainsuggestions(paths, urls):
    domainsuggestions = pd.Series()
    for index in paths.keys():
        if urls[index].domain in domainsuggestions:
            domainsuggestions[urls[index].domain].append(index)
        else:
            domainsuggestions[urls[index].domain] = [index]
    print("domainsuggestions")
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
    
def combinesuggestions(timeproposals, domainsuggestions, urls, amount):
    suggestions = []
    for domain in domainsuggestions.keys()[:1]:
        for d in domainsuggestions[domain][:2]: 
            if d not in suggestions:
                suggestions.append(d)  
    for domain in domainsuggestions.keys()[1:3]:
        for d in domainsuggestions[domain][:1]: 
            if d not in suggestions:             
                suggestions.append(d)
    domains = [x for x in timeproposals.keys() if x not in [y for y in suggestions]]
    for domain in domains:
        if domain in domainsuggestions:  
            for d in domainsuggestions[domain][:1]: 
                if d not in suggestions:
                    suggestions.append(d)
                    break
    if len(suggestions) < amount:
        for domain in domainsuggestions.keys():
            for d in domainsuggestions[domain][:1]: 
                if d not in suggestions:             
                    suggestions.append(d)
                    if len(suggestions) == amount:
                        return suggestions
    return suggestions

def suggestcontinuation(url, urls):
    global F
    dayproposals = proposedaytimes(proposed, 15*60, 10)
    weekproposals = proposeweektimes(proposed, 3)
    timeproposals = combinetimeproposals(dayproposals, weekproposals)
    paths = pd.Series()
    #trail = [[],0]
    breathtraverse(F, [(proposed.link, 0)], paths, 8, 10)
    paths = paths.sort_values(ascending = False)
    domainproposals = domainsuggestions(paths, urls)
    return combinesuggestions(timeproposals, domainproposals, urls, 5)

    
print ("total domains: " + str(len(domains)))
print("----")
proposed = clicks[70]
print("current: " + proposed.link)

suggestions = suggestcontinuation(proposed, urls)
for click in clicks[71:79]:
    print(click.link)
print("-----------------------------")
for sug in suggestions:
    print(sug)




        


    
    
    







