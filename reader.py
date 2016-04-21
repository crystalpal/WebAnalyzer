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
import pandas as pd
import os



file = 'C:/Users/Joren/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test.csv'
file1 = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_16J.csv'
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
    add = False
    if action.timestamp - lastnode.timestamp > 60*60: # in seconds = 1 hour
            trails.append([])
            intertrails.append((lastnode, action))                  
    else:       
        if action.action == "load":
            loads.append(action)
            if len(clicks) < 1 or not action.domain == clicks[-1].domain:
                add = True
        if action.action == "click" or add:
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
                if not (previous, action) in F:
                    F.add_edge(previous, action, weight=0, trails = set())
                trails[-1].append((previous, action, time))
                F[previous][action][0]['weight'] += 3 
                F[previous][action][0]['trails'].add(len(trails))
                dom1 = domains[previous.domain]
                dom2 = domains[action.domain]
                weekday = tm.gmtime(action.timestamp).tm_wday
                if dom2 in weekdays[weekday].keys():
                    val = weekdays[weekday].get_value(dom2) + 1
                    weekdays[weekday].set_value(dom2, val)  
                else:
                    weekdays[weekday].set_value(dom2, 1)
                weekdays[weekday] = weekdays[weekday].sort_values(ascending = False)
                if not dom1.dom == dom2.dom:                    
                    #addtotime(tm.gmtime(action.timestamp).tm_hour+1, dom2)
                    daytime.add(dom2, action.timestamp)
                    G.add_edge(dom1, dom2)   
    lastnode = action
    
    
def gettime(hour):
    if 7 <= hour < 10:
        return daytime[0]
    elif 10 <= hour < 12:
        return daytime[1]
    elif 12 <= hour < 14:
        return daytime[2]
    elif 14 <= hour < 16:
        return daytime[3]
    elif 16 <= hour < 18:
        return daytime[4]
    elif 18 <= hour < 22:
        return daytime[5]
    elif hour > 22 or hour <= 1:
        return daytime[6]
    else:
        return daytime[7]
        
def addtotime(hour, action):
    timeday = gettime(hour)
    if action in timeday.keys():
        val = timeday.get_value(action) + 1
        timeday.set_value(action, val)
    else:
        timeday.set_value(action, 1)
    timeday = timeday.sort_values(ascending = False)
                
def traverse(G, source, current, maxi, trail, paths):
    if current == maxi:
        return
    for n in G.neighbors(source):
        if n.timestamp - source.timestamp < 20:
            traverse(G, n, current, maxi, trail, paths)
        else:
            score = calculatescore(F, source, n, current)
            trail[0].append(n)
            trail[1] += score
            paths.append(copy.deepcopy(trail))   
            current += 1
            traverse(G, n, current, maxi, trail, paths)
            
def proposeweektimes(amount):
    #return weekdays[datetime.datetime.today().weekday()][:amount]
    return weekdays[0][:amount]
def proposedaytimes(amount):
    #return gettime(datetime.datetime.today().hour)[:amount]
    return gettime(23)[:amount]
        
        
def calculatescore(F, source, neighbor, current):
    return F[source][neighbor][0]['weight']*0.8

#line_prepender(file2, 'time,action,link,other')  


f = open(file1)
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
path = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/u1'
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
print ("total domains: " + str(len(domains)))
print("----")
proposed = clicks[0]

paths = []
trail = [[],0]
'''      
traverse(F, proposed, 0, 3, trail, paths)
for trail in paths:
    for node in trail[0]:
        print(node.link)
    print(trail[1])
'''    
times = proposeweektimes(3)
print("days")
for i in range(0, len(times.keys())):
    print(times.keys()[i].dom + " " + str(times[i]))
    '''
daytimes = proposedaytimes(3)
print("times")
for i in range(0, len(daytimes.keys())):
    print(daytimes.keys()[i].dom + " " + str(daytimes[i]))
'''
print(calendar.timegm(tm.gmtime()))
daytimes = daytime.getrange(calendar.timegm(tm.gmtime()), 60*30)
print("times")
for i in range(0, len(daytimes.keys())):
    print(daytimes.keys()[i] + " " + str(daytimes[i]))
print(len(domains))
print(len(clicks))
print(len(trails))