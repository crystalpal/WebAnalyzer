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



file = 'C:/Users/Joren/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test.csv'
file1 = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_13.csv'
file2 = 'C:/Users/Joren/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_22.csv'

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
        
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        content = content.replace(", ", ",")
        content = content.replace('"', "")
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') +  '\n' + content)
        
inputline = "2016-03-13T09:31:16.062Z,load,https://www.google.be/?gws_rd=ssl,"

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
    if action.action == "load":
        loads.append(action)
    elif action.action == "click":
        clicks.append(action)
        #check how far the last unloaded page was in the past, and start a new trail if necessary
        if action.timestamp - lasttime[0] > 20:#60*60: # in seconds = 1 hour
            nboftrails[0] += 1
        #check if the domain is already known in the system, if not initialize
        if not action.domain in domains.keys():
            domains[action.domain] = Domain(action.domain)
        domains[action.domain].urls.append(action)
        if len(clicks) > 1:
            previous = clicks[-2]
            linknodes[action.link] = action
            time = action.timestamp - previous.timestamp
            if time > maxtime[0]:
                maxtime[0] = time
            edges.append((previous, action, nboftrails[0]))
            F.add_edge(previous, action, weight=5, trail=nboftrails[0])
            dom1 = domains[previous.domain]
            dom2 = domains[action.domain]
            if not dom1.dom == dom2.dom: 
                domainedges.append((dom1, dom2, nboftrails[0]))
                G.add_edge(dom1, dom2, trail = nboftrails[0])   
    lasttime[0] = action.timestamp
                
        
#line_prepender(file1, 'time,action,link,other')  


f = open(file2)
#data = csv.reader(f, delimiter=',')
data = f

loads = []
clicks = [] # A list containing every click action
domains = {} # A dictionary mapping domain names on domain objects
edges = [] # A list containing all edges bewteen (click)nodes
domainedges = [] # A list containing all edges between domains
linknodes = {} # A dictionnary mapping urls on action objects   
maxtime = [0] # The masimum time that is spent on a single url
domaintime = [0] # The maximum time that is spent in a domain // note, change both or add to trailtime 
nboftrails = [0] # The total number of trails, acts as a counter
trails = {} # A dictionnary mapping each trailid to a time? spent in that trail?
lasttime = [tm.mktime(tm.strptime("1980 1 1 1 1 1", "%Y %m %d %H %M %S"))]

plt.figure(figsize=(10,10))
plt.axis('off') 
F = nx.MultiDiGraph()
G = nx.MultiDiGraph()

iterrows = iter(data)
next(iterrows)
for row in iterrows:
    parseClick(str(row)) 
    
print("trails " +  str(nboftrails[0]))
    
#F.add_edges_from(edges)
nodevalues = [node.color for node in F.nodes()]
nodelabels = {clicks[node]:clicks[node].domain[clicks[node].domain.index('//')+2:] for node in range(0, len(F.nodes()))}
nodepos = nx.fruchterman_reingold_layout(F)
nodesizes = [(F.nodes()[index+1].timestamp - F.nodes()[index].timestamp)/maxtime[0]*1000 for index in range(0, len(F.nodes())-1)]
nx.draw_networkx_nodes(F, nodepos, cmap=plt.get_cmap('jet'), node_color = nodevalues, node_size=nodesizes)
nx.draw_networkx_edges(F, nodepos, edgelist=edges, arrows=True)
nx.draw_networkx_labels(F, nodepos, nodelabels ,font_size=15)
plt.show() 
    

plt.figure(figsize=(10,10))
plt.axis('off') 
values = [colorConverter.to_rgba('y', alpha = index/(len(G.nodes()))) for index in range(0, len(G.nodes()))]
labels = {domains[node]:node for node in domains}
pos = nx.fruchterman_reingold_layout(G)
sizes = [len(node.urls)*1000 for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color = values, node_size=sizes)
nx.draw_networkx_edges(G, pos, edgelist=domainedges, arrows=True)
nx.draw_networkx_labels(G, pos, labels ,font_size=10)

#plt.show()
print ("total domains: " + str(len(domains))) 

proposedlink = clicks[5].link
print(clicks[4].link)
print(proposedlink)
print(clicks[6].link)
print("---")

for n in F.neighbors(linknodes[proposedlink]):
    print(n.link)
    for nn in F.neighbors(n):
        print(nn.link)

print("----")
nexts = nx.single_source_shortest_path_length(F ,source=n, cutoff=5)
print(nexts)
for ns in nexts:
    print(ns.link)



        
    
