import networkx as nx
import time
import os
import argparse
import NPA
import utils
from queue import Queue

def getNbrMap(hypergraph, v,g):
    neighbor_counts = {}
    for hyperedge in hypergraph.nodes[v]['hyperedges']:
        # Increment the count for each neighbor in the hyperedge
        for neighbor in hyperedge:
            if neighbor != v:
                neighbor_counts[neighbor] = neighbor_counts.get(neighbor, 0) + 1

    filtered_neighbors = {neighbor: count for neighbor, count in neighbor_counts.items() if count >= g}


    return filtered_neighbors

def reorganise(cores):
    D = {}

    for (k, g) in cores.keys():
        V = cores[(k, g)].copy()
        if (k + 1, g) in cores:
            V -= cores[(k + 1, g)]
        if (k, g + 1) in cores:
            V -= cores[(k, g + 1)]
        if V:
            D[(k, g)] = V
    return D

def run(H):
    cores = {}
    g = 1
    while True:
        k = 1
        changed = False
        C = {}
        current_core = set(H.nodes)
        for v in H.nodes:
            Nc_v = getNbrMap(H, v, g)
            C[v] = len(Nc_v)
        while True:
            VQ = Queue()
            for v in current_core:
                if C[v] < k:
                    VQ.put(v)
            while not VQ.empty():
                v = VQ.get()
                current_core.remove(v)
                for w in getNbrMap(H, v, g):
                    if w in current_core:
                        C[w] -= 1
                        if C[w] < k and w not in VQ.queue:
                            VQ.put(w)
            if current_core:
                cores[(k, g)] = current_core.copy()
                changed = True
            else:
                break
            k += 1
        if not changed:
            break
        g += 1
        cores = reorganise(cores)

    return cores

