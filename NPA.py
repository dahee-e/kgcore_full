import networkx as nx
import time
import os
import argparse
import utils
from queue import Queue

def construct_neighbor_occurrence_map(hypergraph, g, k, VQ):
    neighbor_occurrence_map = {}

    for node in hypergraph.nodes:
        neighbor_counts = {}

        # For each hyperedge containing the current node
        for hyperedge in hypergraph.nodes[node]['hyperedges']:
            # Increment the count for each neighbor in the hyperedge
            for neighbor in hyperedge:
                if neighbor != node:
                    neighbor_counts[neighbor] = neighbor_counts.get(neighbor, 0) + 1

        # Filter neighbors that appear in at least g common hyperedges
        filtered_neighbors = {neighbor: count for neighbor, count in neighbor_counts.items() if count >= g}

        # Add the filtered map to the overall map
        neighbor_occurrence_map[node] = filtered_neighbors
        if len(neighbor_occurrence_map.get(node)) < k:
            VQ.put(node)
    return neighbor_occurrence_map,VQ


def run(hypergraph, k, g):

    # Step 2: Initialization
    H = set(hypergraph.nodes())
    VQ = Queue()
    visited = set()
    neighbor_occurrence_map, VQ = construct_neighbor_occurrence_map(hypergraph, g,k,VQ)
    while not VQ.empty():
        v = VQ.get()
        if v not in H:
            continue
        H.remove(v)
        neighbour_list = neighbor_occurrence_map.get(v)
        for nid in neighbour_list:
            neighbor_occurrence_map[nid].pop(v)
            if len(neighbor_occurrence_map.get(nid)) < k :
                VQ.put(nid)
        del neighbor_occurrence_map[v]

    return hypergraph.subgraph(H)