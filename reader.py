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



file = 'C:/Users/Joren/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test.csv'
file1 = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_13.csv'
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
        
        
Edge = namedtuple("Edge", ["previous", "current"])
        
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
    row = inputline.split(',')
    timestamp = row[0]
    act = row[1]
    link = row [2]
    domain = link[:link.index('/', 12)]
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
            
    else:       
        if action.action == "load":
            loads.append(action)
        elif action.action == "click":
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
                F[previous][action][0]['weight'] += 1  
                F[previous][action][0]['trails'].add(len(trails))
                dom1 = domains[previous.domain]
                dom2 = domains[action.domain]
                if not dom1.dom == dom2.dom:
                    G.add_edge(dom1, dom2)   
    lastnode = action
                
        
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
lastnode = Action(None, None, None, tm.strptime("1980 1 1 1 1 1", "%Y %m %d %H %M %S"), None)

plt.figure(figsize=(10,10))
plt.axis('off') 
F = nx.MultiDiGraph()
G = nx.MultiDiGraph()

iterrows = iter(data)
next(iterrows)
for row in iterrows:
    parseClick(str(row))
print("----------")
print(len(trails))
for nb in range(0, len(trails)):
    print("trail " + str(nb))
    for (start, end, time) in trails[nb]:
        print(start.link)


    
#F.add_edges_from(edges)
nodevalues = [node.color for node in F.nodes()]
nodelabels = {clicks[node]:clicks[node].domain[clicks[node].domain.index('//')+2:] for node in range(0, len(F.nodes()))}
nodepos = nx.fruchterman_reingold_layout(F)
nodesizes = [(F.nodes()[index+1].timestamp - F.nodes()[index].timestamp)/maxtime*1000 for index in range(0, len(F.nodes())-1)]
nx.draw_networkx_nodes(F, nodepos, cmap=plt.get_cmap('jet'), node_color = nodevalues, node_size=nodesizes)
nx.draw_networkx_edges(F, nodepos, arrows=True)
nx.draw_networkx_labels(F, nodepos, nodelabels ,font_size=15)
plt.show() 
    

plt.figure(figsize=(10,10))
plt.axis('off') 
values = [colorConverter.to_rgba('y', alpha = index/(len(G.nodes()))) for index in range(0, len(G.nodes()))]
labels = {domains[node]:node for node in domains}
pos = nx.fruchterman_reingold_layout(G)
sizes = [len(node.urls)*1000 for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color = values, node_size=sizes)
nx.draw_networkx_edges(G, pos, arrows=True)
nx.draw_networkx_labels(G, pos, labels ,font_size=10)

#plt.show()
print ("total domains: " + str(len(domains))) 
'''
proposedlink = clicks[5].link
print(clicks[4].link)
print(proposedlink)
print(clicks[6].link)
print("---")

for n in F.neighbors(urls[proposedlink]):
    print(n.link)
    for nn in F.neighbors(n):
        print(nn.link)

print("----")
nexts = nx.single_source_shortest_path_length(F ,source=n, cutoff=5)
print(nexts)
for ns in nexts:
    print(ns.link)
'''


        
    
