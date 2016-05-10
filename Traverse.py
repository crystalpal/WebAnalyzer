# -*- coding: utf-8 -*-
"""
taverse.py

@author: Joren & Vincent

"""
from utilities import addtopath


def dtraverse(G, source, current, maxi, trail, paths):
    if current == maxi:
        return
    for n in G.neighbors(source):
        if n.timestamp - source.timestamp < 20:
            dtraverse(G, n, current, maxi, trail, paths)
        else:
            score = G[source.link][n.link][0]['weight']
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
                queue.append((n, current))
    breathtraverse(G, queue, paths, maxdepth, lookaheadtime)
