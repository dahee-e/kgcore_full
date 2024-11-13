import networkx as nx
import time
import os
import argparse
import utils

def construct_neighbor_occurrence_map(hypergraph, g):
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

    return neighbor_occurrence_map


def run(hypergraph, k, g):

    # Step 2: Initialization
    H = set(hypergraph.nodes())
    neighbor_occurrence_map = construct_neighbor_occurrence_map(hypergraph, g)

    changed = True
    while changed:
        changed = False

        marked_nodes = set()

        for v in H:
            if len(neighbor_occurrence_map.get(v)) < k:
                marked_nodes.add(v)
                changed = True

        for w in marked_nodes:
            H.remove(w)
            neighbour_list = neighbor_occurrence_map.get(w)
            for nid in neighbour_list:
                neighbor_occurrence_map[nid].pop(w)
            hypergraph.remove_node(w)

    return hypergraph.subgraph(H)