# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 14:41:32 2016

@author: Joren & Vincent
"""
import networkx as nx
import matplotlib.pyplot as plt
import time as tm
import copy
import datetime
import pandas as pd
import os
import sys
from datastructures import Action, Domain, CircularList
from utilities import combinetimeproposals, domainsuggestions, combinesuggestions
from traverse import breathtraverse


class Proposer(object):

    def __init__(self, path):
        self.clicks = []   # A list containing every click action
        self.domains = {}  # A dictionary mapping domain names on domain objs
        self.urls = {}     # A dictionnary mapping urls on action objects
        self.maxtime = 0   # The masimum time that is spent on a single url
        # The maximum time spent in a domain
        # // note, change both or add to trailtime
        self.domaintime = 0
        self.trails = [0]  # A list of trailid's containing their urls
        self.trails[0] = []
        self.intertrails = []
        self.weekdays = {0: pd.Series(), 1: pd.Series(), 2: pd.Series(),
                         3: pd.Series(), 4: pd.Series(), 5: pd.Series(),
                         6: pd.Series()}
        self.daytime = CircularList()
        self.lastnode = Action(None, None, None, None, 
                               tm.strptime("1980 1 1 1 1 1", "%Y %m %d %H %M %S"),
                               None)

        self.F = nx.MultiDiGraph()
        self.G = nx.MultiDiGraph()

        # Colors for graph representation
        self.colors = ["red", "blue", "yellow", "green", "purple", "white",
                       "orange", "pink", "gray", "brown", "white", "silver",
                       "gold", "red", "blue", "yellow", "green", "purple",
                       "white", "orange", "pink", "gray", "brown", "white",
                       "silver", "gold", "red", "blue", "yellow", "green",
                       "purple", "white", "orange", "pink", "gray", "brown",
                       "white", "silver", "gold"]

        self.fillstructures(path)

    def clean_file_row(self, input):
        """ Cleans the input string from double quotes, \n and whitespaces """
        input = input.rstrip()
        input = "".join(input.split())
        input = input.replace("\"", "")
        return input

    def fillstructures(self, path):
        """ Read out all csv data files from a given directory """
        print("Reading all previous data files...")
        count = 0
        for file in os.listdir(path):
            try:
                iterrows = iter(open(path + "/"+file))
                for row in iterrows:
                    row = self.clean_file_row(row)
                    # If an empty row (eg end of file) or JS link
                    if not row and "javascript" not in row.lower():
                        continue
                    self.parseClick(str(row))
            except:  # If an import still fails, skip & keep count
                count += 1
                print("Skipped file ", file)
        print("Finished reading, skipped files:", count)

    def parseClick(self, inputline):
        action = self.extractAction(inputline)
        if action is not None:
            self.insertAction(self.F, self.G, action)

    def extractAction(self, inputline):
        #Parse inputline from default csv format and extract an Action object from it
        row = self.clean_file_row(inputline).split(',')
        timestamp = row[0]
        act = row[1]
        if not act == "click" or "//" not in row[3]:
            return None
        previous = row[2]
        link = row[3]
        # Parse timestamp - everything except for miliseconds after the dot
        timefmt = tm.strptime(timestamp.split('.')[0], "%Y-%m-%dT%H:%M:%S")        
        #check if this is the first action in a sequence, first link might not have been registered as an action     
        if len(self.clicks) == 0:
            self.create_action(act, None, previous, timefmt)
        currentaction = self.create_action(act, previous, link, timefmt)
        return currentaction
        
    def create_action(self, act, previous, link, timefmt):
         domain_index = link.index('//') + 2
         domain = link[domain_index:link.index('/', domain_index)]
         domain = domain.replace("www.", "")[:domain.rindex('.')]         
         if "google" in link and "&" in link:
             link = link[0:link.index('&')]
         if domain not in self.domains.keys():
             self.domains[domain] = Domain(domain)
         clickaction =  Action(act, self.domains[domain], previous, link, timefmt, self.colors[len(self.clicks) % 9])
         if clickaction.link not in self.domains[domain].urls.keys():
            clickaction.domain.urls.set_value(clickaction.link, 1)
         else:
            self.domains[domain].urls[clickaction.link] += 1        
         self.domains[domain].urls.sort_values(ascending=False)
         return clickaction

    def insertAction(self, G, D, action):
        # check how far the last unloaded page was in the past, and start a new trail if necessary
        if action.timestamp - self.lastnode.timestamp > 60*60:  # seconds = 1 hr
            self.trails.append([])
            self.intertrails.append((self.lastnode, action))
        self.clicks.append(action)
        # check if the domain is already known in the system, if not initialize        
        if len(self.clicks) > 1:
            previous = self.clicks[-2]
            self.urls[action.link] = action
            time = action.timestamp - previous.timestamp
            if time > self.maxtime:
                self.maxtime = time
            if not (previous.link, action.link) in G.edges():
                G.add_edge(previous.link, action.link, weight=0, time=0, trails=set())
            self.trails[-1].append((previous, action, time))
            G[previous.link][action.link][0]['weight'] += 1
            G[previous.link][action.link][0]['time'] = (G[previous.link][action.link][0]['time'] + time)/2
            G[previous.link][action.link][0]['trails'].add(len(self.trails))
            dom1 = previous.domain
            dom2 = action.domain
            weekday = tm.gmtime(action.timestamp).tm_wday
            if dom2.dom in self.weekdays[weekday].keys():
                val = self.weekdays[weekday].get_value(dom2.dom) + 1
                self.weekdays[weekday].set_value(dom2.dom, val)
            else:
                self.weekdays[weekday].set_value(dom2.dom, 1)
            self.weekdays[weekday] = self.weekdays[weekday].sort_values(ascending=False)
            if not dom1.dom == dom2.dom:
                self.daytime.add(dom2, action.timestamp)
                D.add_edge(dom1, dom2)
        self.lastnode = action

    def parseAction(self, inputline):
        action = self.extractAction(inputline)
        if action is None:
            return None
        self.insertAction(self.F, self.G, action)
        return self.suggestcontinuation(action)

    def suggestcontinuation(self, action):
        print(action.link)
        print(action.domain.dom)
        print("urls in domain")
        print(action.domain.urls)
        dayproposals = self.proposedaytimes(action.timestamp, 15*60, 10)
        weekproposals = self.proposeweektimes(action.timestamp, 3)
        timeproposals = combinetimeproposals(dayproposals, weekproposals)
        paths = pd.Series()
        # trail = [[],0]
        breathtraverse(self.F, [(action.link, 0)], paths, 3, 10)
        paths = paths.sort_values(ascending=False)
        domainproposals = domainsuggestions(paths, self.urls)
        return combinesuggestions(action, timeproposals, domainproposals, self.urls, 5)        

    def suggeststart(self):
        dayproposals = self.proposedaytimes(datetime.datetime.utcfromtimestamp(tm.time()), 15*60, 10)
        weekproposals = self.proposeweektimes(datetime.datetime.utcfromtimestamp(tm.time()), 3)
        timeproposals = combinetimeproposals(dayproposals, weekproposals)
        trailproposals = [x.domain for (y, x) in self.intertrails]
        proposals = []
        domainproposals = []
        for timeproposal in timeproposals:
            if timeproposal in trailproposals:
                domainproposals.append(timeproposal)
        for domain in domainproposals[:2]:
            domainlinks = [y.link for (y, x) in self.intertrails if x == domain]
            linkproposals = [(link, sum(self.F.edges(link)['weight'])) for link in domainlinks]
            sortedprops = linkproposals.sort(key=lambda tup: tup[1])
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
