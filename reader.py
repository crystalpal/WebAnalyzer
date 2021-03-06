# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 14:41:32 2016

@author: Joren & Vincent
"""
import networkx as nx
import matplotlib.pyplot as plt
import time as tm
import datetime
import pandas as pd
import os
from datastructures import Action, Domain, CircularList
from utilities import combine_timeproposals, domain_suggestions
from utilities import combine_suggestions, parse_timestamp
from Traverse import breathtraverse


class Proposer(object):

    def __init__(self, path, fillstructures=True):
        self.clicks = []   # A list containing every click action
        self.domains = pd.Series()  # A dictionary mapping domain names on domain objs
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
        self.lastnode = Action(None, None, None, None, None, None)

        self.F = nx.MultiDiGraph()  # Graph for all the URLs
        self.G = nx.MultiDiGraph()  # Graph for all the domains

        # Colors for graph representation
        self.colors = ["red", "blue", "yellow", "green", "purple", "white",
                       "orange", "pink", "gray", "brown", "white", "silver",
                       "gold", "red", "blue", "yellow", "green", "purple",
                       "white", "orange", "pink", "gray", "brown", "white",
                       "silver", "gold", "red", "blue", "yellow", "green",
                       "purple", "white", "orange", "pink", "gray", "brown",
                       "white", "silver", "gold"]

        if fillstructures:
            self.fillstructures(path)

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
                    self.parse_action(str(row), file_action=True)
            except:  # If an import still fails, skip file & keep count
                count += 1
                print("Skipped file:", file)
        print("Finished reading, skipped files:", count)

    def clean_file_row(self, input):
        """ Cleans the input string from double quotes, \n and whitespaces """
        input = input.rstrip()
        input = "".join(input.split())
        input = input.replace("\"", "")
        return input

    def parse_action(self, inputline, file_action=False, suggest_amount=5):
        """ Gives N suggestions from a comma seperated inputline """
        row = self.clean_file_row(inputline).split(',')
        act = row[1]

        if act=="load" and not file_action and self.lastnode.link is not None:
            if not self.lastnode.link == row[2]:
                row[1] = "click"
                act = "click"
                row[3] = row[2]
                row[2] = self.lastnode.link
                print("Generated click", row[2], "->", row[3], sep=" ")

        # If a load action, return suggestions
        if act == "load":
            domain = self.get_domain(row[2])
            self.insert_in_timelists(domain, parse_timestamp(row[0]))
            if self.lastnode.domain is None:
                self.lastnode.update_link(row[2], self.domains[domain])
            if not file_action:
                return self.suggest_continuation(self.lastnode, suggest_amount)

        # Ignore everything but (valid) click actions
        if not act == "click" or "//" not in row[3]:
            return None
        action = self.extract_action(row)
        self.insert_action(self.F, self.G, action, file_action=file_action)
        # Note: Ideally, only load events should give suggestions feedback
        # But with the growing amount of JavaScript websites (e.g. YouTube)
        # Only the initial load triggers this event
        if not file_action:
            return self.suggest_continuation(action, suggest_amount)

    def extract_action(self, row):
        """ Extracts and parses the different parts (eg. action)
        of the comma seperated (default csv format) input """
        timestamp = parse_timestamp(row[0], seconds=False)
        act = row[1]
        previous = row[2]
        link = row[3]
        # check if this is the first action in a sequence,
        # first link might not have been registered as an action
        if len(self.clicks) == 0:
            self.create_action(act, None, previous, timestamp)
        current_action = self.create_action(act, previous, link, timestamp)
        return current_action

    def create_action(self, act, previous, link, timefmt):
        domain = self.get_domain(link)
        clickaction = Action(act, self.domains[domain], previous, link,
                              timefmt, self.colors[len(self.clicks) % 9])
        clickaction.domain.addurl(clickaction.link)
        return clickaction

    def insert_in_timelists(self, domain, timestamp):
        """ Insert the loaded domain in the time-based suggestion lists """
        domain = self.domains[domain]
        # Add to a time-of-day list
        self.daytime.add(domain.dom, timestamp)
        # Add to a day-of-week list
        wd = tm.gmtime(timestamp).tm_wday
        val = 1
        if domain.dom in self.weekdays[wd].keys():
            val = self.weekdays[wd].get_value(domain.dom) + val
        self.weekdays[wd].set_value(domain.dom, val)
        # Sort on occurence count
        self.weekdays[wd] = self.weekdays[wd].sort_values(ascending=False)

    def get_domain(self, link):
        """ Get domain from link and add to the pandas domain list """
        domain_index = link.index('//') + 2
        domain = link[domain_index:link.index('/', domain_index)]
        domain = domain.replace("www.", "")  # [:domain.rindex('.')]
        if "google" in link and "&" in link:
            link = link[0:link.index('&')]
        if domain not in self.domains.keys():
            self.domains[domain] = Domain(domain)
        return domain

    def insert_action(self, url_graph, dom_graph, action, file_action=False):
        # check how far the last unloaded page was in the past
        # and start a new trail if necessary
        if action.timestamp - self.lastnode.timestamp > 60*60:  # 1 hr in sec
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
            if not (previous.link, action.link) in url_graph.edges():
                url_graph.add_edge(previous.link, action.link, weight=0,
                                   totaltime=0, avgtime=0, trails=set())
            self.trails[-1].append((previous, action, time))
            g_edge = url_graph[previous.link][action.link][0]
            g_edge['weight'] += 1
            g_edge['totaltime'] += time
            g_edge['avgtime'] = g_edge['totaltime']/g_edge['weight']
            g_edge['trails'].add(len(self.trails))
            dom1 = previous.domain
            dom2 = action.domain
            if not dom1.dom == dom2.dom:
                dom_graph.add_edge(dom1, dom2)
        if not file_action:  # Only websites from a current action
            self.lastnode = action
        self.insert_in_timelists(action.domain.dom, action.timestamp)

    def suggest_continuation(self, action, suggestion_amount):
        """ Gathers site proposals based on time, popular domains and current
        click stream """
        dayproposals = self.propose_daytimes(action.timestamp, 45)
        weekproposals = self.propose_weektimes(action.timestamp)
        timeproposals = combine_timeproposals(dayproposals, weekproposals)
        paths = pd.Series()
        # trail = [[],0]
        breathtraverse(self.F, [(action.link, 0)], [], paths, 1, 4)
        paths = paths.sort_values(ascending=False)
        domainproposals = domain_suggestions(paths, self.urls)
        suggestions = combine_suggestions(action,
                                          timeproposals[:10],
                                          domainproposals[:10],
                                          self.urls,
                                          self.domains,
                                          suggestion_amount)
        # sys.exit()
        return suggestions

    def suggest_start(self, amount):
        utc_timestamp = datetime.datetime.utcfromtimestamp(tm.time())
        dayproposals = self.propose_daytimes(utc_timestamp, 25*60)
        weekproposals = self.propose_weektimes(utc_timestamp)
        timeproposals = combine_timeproposals(dayproposals,
                                              weekproposals,
                                              amount)
        trailproposals = [x.domain for (y, x) in self.intertrails]
        proposals = []
        domainproposals = []
        for timeproposal in timeproposals:
            if timeproposal in trailproposals:
                domainproposals.append(timeproposal)
        for domain in domainproposals[:2]:
            dl = [y.link for (y, x) in self.intertrails if x == domain]
            linkproposals = [(l, sum(self.F.edges(l)['weight'])) for l in dl]
            sortedprops = linkproposals.sort(key=lambda tup: tup[1])
            proposals.append(sortedprops[:2])
        return proposals

    def propose_weektimes(self, timestamp):
        """ Proposes all the domains (in pandas.Series) that occure more or
        equal to their average occurence during the rest of the week """
        weekday = datetime.datetime.utcfromtimestamp(timestamp).weekday()
        tday = self.weekdays[weekday]
        # Get the total count of all domains for all days except today
        dailyavg = pd.Series()
        for day in [x for x in range(7) if x != weekday]:
            oday = self.weekdays[day]
            for domain in set(oday.keys()).intersection(tday.keys()):
                if domain not in dailyavg.keys():
                    dailyavg.set_value(domain, oday[domain])
                else:
                    dailyavg[domain] += oday[domain]
        possibledomains = pd.Series()
        for domain in tday.keys():
            if domain in dailyavg.keys():
                if tday[domain] > dailyavg[domain]/6:
                    possibledomains.set_value(domain, tday[domain])
            else:
                possibledomains.set_value(domain, tday[domain])
        return possibledomains

    def propose_daytimes(self, timestamp, r):
        bef = self.daytime.getrangearound(timestamp-2*r, r)
        after = self.daytime.getrangearound(timestamp+2*r, r)
        bef.add(after)
        current = self.daytime.getrangearound(timestamp, r)
        possibledomains = pd.Series()
        for domain in current.keys():
            if domain in bef.keys() and current[domain] > bef[domain]*3/5:
                possibledomains.set_value(domain, current[domain])
        return possibledomains 


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
