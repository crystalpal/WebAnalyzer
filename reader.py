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
file1 = 'F:/Dropbox/Vince - Joren/Master Ai/Machine Learning - Project/Datasets/test/march_13.csv'

colors = ["red", "blue", "yellow", "green", "purple", "black", "orange", "pink", "gray", "brown", "white", "silver", "gold", 
          "red", "blue", "yellow", "green", "purple", "black", "orange", "pink", "gray", "brown", "white", "silver", "gold"          
          "red", "blue", "yellow", "green", "purple", "black", "orange", "pink", "gray", "brown", "white", "silver", "gold"]  
    
class Action(object):
    action =""
    domain = ""
    link = ""
    timestamp = ""
    color = ""
    def __init__(self, action, domain, link, timeformat):
        self.action = action
        self.domain = domain
        self.link = link
        self.timestamp = timeformat
        
    def timedifference(self, action):
        time = tm.mktime(action.timestamp) - tm.mktime(self.timestamp)
        return tm.mktime(action.timestamp) - tm.mktime(self.timestamp)
        
class Domain(object):
    url = ""
    color = ""
    def __init__(self, url, color):
        self.dom = url
        self.color = color
    
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
doms = []
d = []


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
    action = Action(act, domain, link, timeformat)
    if act == "load":
        loads.append(action)
    if act == "click":
        clicks.append(action)
    if not action.domain in d:
        dom = Domain(action.domain, colors[len(doms)])
        doms.append(dom)
        d.append(action.domain)
   
nodes = [] 
domains = []
domainedges = []
maxtime = 0  
for i in range(0, len(clicks)-1):
    nodes.append((clicks[i], clicks[i+1])) 
    time = clicks[i].timedifference(clicks[i+1])
    if time > maxtime:
        maxtime = time
   
for i in range(0, len(doms)-1):
    domains.append((doms[i], doms[i+1]))
     
         
edges = []
for node in nodes:
    time = node[0].timedifference(node[1])
    edges.append((node[0], node[1], time/maxtime))


colormapping = dict(zip(domains, colors))

domainmapping = {}
for color in colormapping:
    domainmapping[color] = []
    
plt.figure(figsize=(10,10))
plt.axis('off') 
G = nx.MultiDiGraph()
#G.add_edges_from(nodes)
G.add_edges_from(domains)
values = [node.color for node in G.nodes()]
#labels = {clicks[node]:node for node in range(0, len(G.nodes()))}
labels = {doms[node]:node for node in range(0, len(G.nodes()))}
pos = nx.fruchterman_reingold_layout(G)
gnodes = nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_color = values, node_size=2000)
#nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='r', arrows=True)
#gedges = nx.draw_networkx_edges(G, pos, edgelist=nodes, arrows=True)
for start, end in domainedges:
    # You can attach any attributes you want when adding the edge
    G.add_edge(start, end)
#nx.draw_networkx_edges(G, pos, edgelist=edges, arrows=True, length=labels)
nx.draw_networkx_edges(G, pos, edgelist=domains, arrows=True)
nx.draw_networkx_labels(G, pos, labels, font_size=20)

plt.show()
print ("total domains: " + str(len(domainmapping))) 




        
    
