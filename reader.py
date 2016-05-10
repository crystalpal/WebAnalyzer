# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 14:41:32 2016

@author: Joren
"""
import networkx as nx
import matplotlib.pyplot as plt
import time as tm
import copy
import datetime
import pandas as pd
import os
import sys
from DataStructures import Action, Domain, CircularList
from Utilities import combinetimeproposals, domainsuggestions, combinesuggestions
from Traverse import breathtraverse

class Proposer(object):
    
    def __init__(self, path):
        self.clicks = [] # A list containing every click action
        self.domains = {} # A dictionary mapping domain names on domain objects
        self.urls = {} # A dictionnary mapping urls on action objects   
        self.maxtime = 0 # The masimum time that is spent on a single url
        self.domaintime = 0 # The maximum time that is spent in a domain // note, change both or add to trailtime 
        self.trails = [0] # A list of trailid's containing their urls
        self.trails[0] = []
        self.intertrails = []
        self.weekdays = {0:pd.Series(), 1:pd.Series(), 2:pd.Series(), 3:pd.Series(), 4:pd.Series(), 5:pd.Series(), 6:pd.Series()}
        #daytime = {0:pd.Series(), 1:pd.Series(), 2:pd.Series(), 3:pd.Series(), 4:pd.Series(), 5:pd.Series(), 6:pd.Series(), 7:pd.Series()}
        self.daytime = CircularList()
        self.lastnode = Action(None, None, None, tm.strptime("1980 1 1 1 1 1", "%Y %m %d %H %M %S"), None)
            
        self.F = nx.MultiDiGraph()
        self.G = nx.MultiDiGraph()
        
        self.colors = ["red", "blue", "yellow", "green", "purple", "white", "orange", "pink", "gray", "brown", "white", "silver", "gold", 
          "red", "blue", "yellow", "green", "purple", "white", "orange", "pink", "gray", "brown", "white", "silver", "gold"          
          "red", "blue", "yellow", "green", "purple", "white", "orange", "pink", "gray", "brown", "white", "silver", "gold"]  
 
        self.fillstructures(path)
    
           
    def fillstructures(self, path):
        count = 0
        for file in os.listdir(path):
            try:
                iterrows = iter(open(path + "/"+file))
                for row in iterrows:
                    if not row.rstrip():
                        continue
                    self.parseClick(str(row.rstrip()))  
            except:
                count += 1
                print("skipped file ", file)
        print("Skipped files: ",count)
    
    def parseClick(self, inputline):
        action = self.extractAction(inputline)
        self.insertAction(self.F, self.G, action)
    
    def extractAction(self, inputline):
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
        return Action(act, domain, link, timeformat, self.colors[len(self.clicks)%9])

    def insertAction(self, G, D, action):
            #check how far the last unloaded page was in the past, and start a new trail if necessary
        if action.timestamp - self.lastnode.timestamp > 60*60: # in seconds = 1 hour
            self.trails.append([])
            self.intertrails.append((self.lastnode, action))  
                                      
        if action.action == "click":
            self.clicks.append(action)       
            #check if the domain is already known in the system, if not initialize
            if not action.domain in self.domains.keys():
                self.domains[action.domain] = Domain(action.domain)
            self.domains[action.domain].urls.append(action)
            if len(self.clicks) > 1:
                previous = self.clicks[-2]
                self.urls[action.link] = action
                time = action.timestamp - previous.timestamp
                if time > self.maxtime:
                    self.maxtime = time
                if not (previous.link, action.link) in G.edges():
                    G.add_edge(previous.link, action.link, weight=0, time=0, trails = set())
                self.trails[-1].append((previous, action, time))
                G[previous.link][action.link][0]['weight'] += 1
                G[previous.link][action.link][0]['time'] = (G[previous.link][action.link][0]['time'] + time)/2
                G[previous.link][action.link][0]['trails'].add(len(self.trails))
                dom1 = self.domains[previous.domain]
                dom2 = self.domains[action.domain]
                weekday = tm.gmtime(action.timestamp).tm_wday
                if dom2.dom in self.weekdays[weekday].keys():
                    val = self.weekdays[weekday].get_value(dom2.dom) + 1
                    self.weekdays[weekday].set_value(dom2.dom, val)  
                else:
                    self.weekdays[weekday].set_value(dom2.dom, 1)
                self.weekdays[weekday] = self.weekdays[weekday].sort_values(ascending = False)
                if not dom1.dom == dom2.dom:                    
                    self.daytime.add(dom2, action.timestamp)
                    D.add_edge(dom1, dom2)   
        self.lastnode = action
        
    def parseAction(self, inputline):
        action = self.extractAction(inputline)
        self.insertAction(self.F, self.G, action)
        if action.action == "click":
            return self.suggestcontinuation(action)   
    
    def suggestcontinuation(self, action):
        dayproposals = self.proposedaytimes(action.timestamp, 15*60, 10)
        weekproposals = self.proposeweektimes(action.timestamp, 3)
        timeproposals = combinetimeproposals(dayproposals, weekproposals)
        paths = pd.Series()
        #trail = [[],0]
        breathtraverse(self.F, [(action.link, 0)], paths, 8, 10)
        paths = paths.sort_values(ascending = False)
        domainproposals = domainsuggestions(paths, self.urls)
        return combinesuggestions(timeproposals, domainproposals, self.urls, 5)        
        
    def suggeststart(self):
        dayproposals = self.proposedaytimes(datetime.datetime.utcfromtimestamp(tm.time()), 15*60, 10)
        weekproposals = self.proposeweektimes(datetime.datetime.utcfromtimestamp(tm.time()), 3)
        timeproposals = combinetimeproposals(dayproposals, weekproposals)
        trailproposals = [x.domain for (y,x) in self.intertrails]
        
        proposals = []
        domainproposals = []
        for timeproposal in timeproposals:
            if timeproposal in trailproposals:
                domainproposals.append(timeproposal)
        for domain in domainproposals[:2]:
            domainlinks = [y.link for (y,x) in self.intertrails if x == domain]
            linkproposals = [(link, sum(self.F.edges(link)['weight'])) for link in domainlinks]
            sortedprops = linkproposals.sort(key=lambda tup:tup[1])
            proposals.append(sortedprops[:2])
        return proposals
        
    def proposeweektimes(self, timestamp, amount):
        return self.weekdays[datetime.datetime.utcfromtimestamp(timestamp).weekday()][:amount]

    def proposedaytimes(self, timestamp, r, amount):
        return self.daytime.getrange(timestamp, r)[:amount]
                
   
    
   
'''
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
'''

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

plt.show()



   
'''

        


    
    
    







