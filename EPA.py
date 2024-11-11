import networkx as nx
import time
import os
import argparse
import utils
from queue import Queue

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

    for v in H:
        ng = getNbrMap(hypergraph, v, g)
        S[v] = len(ng)
        if S[v] < k:
            VQ.put(v)
            VQ1.add(v)
    while not VQ.empty():
        v = VQ.get()
        ng = getNbrMap(hypergraph, v, g)
        H.remove(v)
        del S[v]
        for w in ng:
            if w not in VQ1:
                S[w] -= 1
                if S[w] < k:
                    VQ.put(w)
                    VQ1.add(w)

    return hypergraph.subgraph(H)
