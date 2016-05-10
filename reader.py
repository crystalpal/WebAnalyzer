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
from Utilities import addtopath, proposedaytimes, proposeweektimes, combinetimeproposals, domainsuggestions, combinesuggestions


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
        
 
    def line_prepender(filename, line):
        with open(filename, 'r+') as f:
            content = f.read()
            content = content.replace(", ", ",")
            content = content.replace('"', "")
            f.seek(0, 0)
            f.write(line.rstrip('\r\n') +  '\n' + content)
    
    def parseClick(self, inputline):
        action = self.extractAction(inputline)
        self.insertAction(action)
    
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

    def insertAction(self, action):
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
                urls[action.link] = action
                time = action.timestamp - previous.timestamp
                if time > self.maxtime:
                    self.maxtime = time
                if not (previous.link, action.link) in F.edges():
                    F.add_edge(previous.link, action.link, weight=0, time=0, trails = set())
                self.trails[-1].append((previous, action, time))
                self.F[previous.link][action.link][0]['weight'] += 1
                self.F[previous.link][action.link][0]['time'] = (self.F[previous.link][action.link][0]['time'] + time)/2
                self.F[previous.link][action.link][0]['trails'].add(len(self.trails))
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
                    self.G.add_edge(dom1, dom2)   
        self.lastnode = action
                
    def dtraverse(self, G, source, current, maxi, trail, paths):
        if current == maxi:
            return
        for n in G.neighbors(source):
            if n.timestamp - source.timestamp < 20:
                self.dtraverse(G, n, current, maxi, trail, paths)
            else:
                score = F[source.link][n.link][0]['weight']
                trail[0].append(n)
                trail[1] += score
                paths.append(copy.deepcopy(trail))   
                current += 1
                self.dtraverse(G, n, current, maxi, trail, paths)
    
    def depthtraverse(self, G, source, paths, current, maxdepth, lookaheadtime):    
        for n in G.neighbors(source):  
            score = G[source][n][0]['weight']
            if G[source][n][0]['time'] < lookaheadtime:
                if current == maxdepth:
                    addtopath(paths, n, score)
                    return
                self.depthtraverse(G, n, paths, (current+1), maxdepth, lookaheadtime)            
            else:
                addtopath(paths, n, score)

    def breathtraverse(self, G, queue, paths, maxdepth, lookaheadtime):
        if len(queue) == 0:
            return
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
        self.breathtraverse(G, queue, paths, maxdepth, lookaheadtime)
            
    def proposeweektimes(self, proposed, amount):
        return self.weekdays[datetime.datetime.utcfromtimestamp(proposed.timestamp).weekday()][:amount]

    def proposedaytimes(self, proposed, r, amount):
        return self.daytime.getrange(proposed.timestamp, r)[:amount]
           
    def fillstructures(self, path):
        for file in os.listdir(path):
            iterrows = iter(open(path + "/"+file))
            for row in iterrows:
                self.parseClick(str(row))
                
    def suggestcontinuation(self, action):
        global F
        global urls
        dayproposals = proposedaytimes(action, 15*60, 10)
        weekproposals = proposeweektimes(action, 3)
        timeproposals = combinetimeproposals(dayproposals, weekproposals)
        paths = pd.Series()
        #trail = [[],0]
        self.breathtraverse(F, [(action.link, 0)], paths, 8, 10)
        paths = paths.sort_values(ascending = False)
        domainproposals = domainsuggestions(paths, urls)
        return combinesuggestions(timeproposals, domainproposals, urls, 5)
    
    def parseAction(self, inputline):
        action = self.extractAction(inputline)
        self.insertAction(action)
        if action.action == "click":
            return self.suggestcontinuation(action)   
   
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

        


    
    
    







