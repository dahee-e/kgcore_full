import networkx as nx
import time
import os
import argparse
import utils
from queue import Queue
import sys
def getNbrMap(hypergraph, node, g):
    cnt = {}

    for hyperedge in hypergraph.nodes[node]['hyperedges']:
        for neighbor in hyperedge:
            if neighbor != node:
                cnt[neighbor] = cnt.get(neighbor,0)+1
    ng = {node: count for node, count in cnt.items() if count >= g}
    return ng

def run(hypergraph, k, g):
    H = set(hypergraph.nodes())
    S = {}
    VQ = Queue()
    VQ1 = set()
    time_report = 0

    for v in H:
        time2 = time.time()
        ng = getNbrMap(hypergraph, v, g)
        time3 = time.time()
        time_report += time3 - time2
        S[v] = len(ng)
        if S[v] < k:
            VQ.put(v)
            VQ1.add(v)
    while not VQ.empty():
        v = VQ.get()
        time2 = time.time()
        ng = getNbrMap(hypergraph, v, g)
        time3 = time.time()
        time_report += time3 - time2
        H.remove(v)
        del S[v]
        for w in ng:
            if w not in VQ1:
                S[w] -= 1
                if S[w] < k:
                    VQ.put(w)
                    VQ1.add(w)

    return hypergraph.subgraph(H), time_report
