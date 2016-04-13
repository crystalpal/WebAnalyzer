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



file = 'C:/Users/Joren/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test.csv'
file1 = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_22.csv'

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
        self.timestamp = timeformat
        self.color = color
        
    def timedifference(self, action):
        time = tm.mktime(action.timestamp) - tm.mktime(self.timestamp)
        return tm.mktime(action.timestamp) - tm.mktime(self.timestamp)
        
class Domain(object):
    url = ""
    color = ""
    urls = []
    def __init__(self, url, color):
        self.dom = url
        self.color = color
        self.urls = []
    
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        content = content.replace(", ", ",")
        content = content.replace('"', "")
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') +  '\n' + content)
        

        
#line_prepender(file1, 'time,action,link,other')  


f = open(file1)
data = csv.reader(f, delimiter=',')

loads = []
clicks = []
domains = {}


iterrows = iter(data)
next(iterrows)
for row in iterrows:
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
    '''    
    datetime = time.struct_time(tm_year=year, tm_mon=month, tm_mday=day, tm_hour=hour, tm_min=minute,
                 tm_sec=second)#, tm_wday=3, tm_yday=335, tm_isdst=-1)
    print (datetime)
    '''
    action = Action(act, domain, link, timeformat, colors[len(clicks)%9])
    if act == "load":
        loads.append(action)
    if act == "click":
        clicks.append(action)
        if not action.domain in domains.keys():
            domains[action.domain] = Domain(action.domain, colors[len(domains.keys())%9])
   
edges = []
domainedges = []
linknodes = {}
for i in range(0, len(clicks)):
    c1 = clicks[i]
    if not c1.link in linknodes:
        linknodes[c1.link] = c1
    if i+1 < len(clicks):
        c2 = clicks[i+1]
        time = c1.timedifference(c2)
        edges.append((c1, c2)) 
        dom1 = domains[c1.domain]
        dom2 = domains[c2.domain]
        if not dom1.dom == dom2.dom: 
            domainedges.append((dom1, dom2))   
    domains[c1.domain].urls.append(c1)


colormapping = dict(zip(domains, colors))
"""
plt.figure(figsize=(10,10))
plt.axis('off') 
G = nx.MultiDiGraph()
G.add_edges_from(domainedges)
values = [node.color for node in G.nodes()]
sizes = [len(node.urls)*1000 for node in G.nodes()]
labels = {first:second.dom for (first, second) in domainedges}
pos = nx.fruchterman_reingold_layout(G)
gnodes = nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_color = values, node_size=sizes)
nx.draw_networkx_edges(G, pos, edgelist=domainedges, arrows=True)
nx.draw_networkx_labels(G, pos, labels ,font_size=10)

#plt.show()
print ("total domains: " + str(len(colormapping))) 

"""
plt.figure(figsize=(10,10))
plt.axis('off') 
F = nx.MultiDiGraph()
F.add_edges_from(edges)
nodevalues = [node.color for node in F.nodes()]
nodelabels = {clicks[node]:node for node in range(0, len(F.nodes()))}
nodepos = nx.fruchterman_reingold_layout(F)
gnodes = nx.draw_networkx_nodes(F, nodepos, cmap=plt.get_cmap('jet'), node_color = nodevalues, node_size=1500)
nx.draw_networkx_edges(F, nodepos, edgelist=edges, arrows=True)
nx.draw_networkx_labels(F, nodepos, nodelabels ,font_size=15)
plt.show()

for start, end in edges:
    F.add_edge(start, end)
    #nx.draw_networkx_edges(G, pos, edgelist=edges, arrows=True, length=labels)

proposedlink = clicks[5].link
print(proposedlink)
print("---")

for n in F.neighbors(linknodes[proposedlink]):
    for nn in F.neighbors(n):
        print(nn.link)



        
    
