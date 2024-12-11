import networkx as nx
import time
import os
import argparse

def get_base(file_path):
    path = os.path.dirname(file_path)
    return path+'/'

def load_hypergraph(file_path):
    hypergraph = nx.Graph()  # Create an empty hypergraph
    E = list()

    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            # Use set to ignore duplicate values in each line and strip whitespace from node names
            if 'instacart' in file_path:
                nodes = {node.strip() for node in line.strip().split(' ')}
            else:
                nodes = {node.strip() for node in line.strip().split(',')}
            nodes = {int(x) for x in  nodes}
            hyperedge = set(nodes)  # Use frozenset to represent the hyperedge
            E.append(hyperedge)
            for node in nodes:
                if node not in hypergraph.nodes():
                    hypergraph.add_node(node, hyperedges=list())  # Add a node for each node
                hypergraph.nodes[node]['hyperedges'].append(hyperedge)  # Add the hyperedge to the node's hyperedge set

    return hypergraph, E



def degree(hypergraph, node):
    neighbors = set()
    for hyperedge in hypergraph.nodes[node]['hyperedges']:
        neighbors.update(hyperedge - {node})  # Collect all nodes in the hyperedge except the current node
    return len(neighbors)

def hyperedges_count(hypergraph, node): # count the number of hyperedges that contain the node
    hyperedges = list()
    for hyperedge in hypergraph.nodes[node]['hyperedges']:
        hyperedges.append(hyperedge)
    return len(hyperedges)

def edge_count(nodes,hyperedges): # Find a hyperedge that contains node
    edges = list()
    for hyperedge in hyperedges:
        if len(hyperedge & set(nodes)) >= 2:
            edges.append(hyperedge)
    return len(edges)

def get_induced_subhypergraph(hypergraph, node_set):
    subhypergraph = nx.Graph()
    for node in node_set:
        if node in hypergraph.nodes:
            subhypergraph.add_node(node, hyperedges=[])
            for hyperedge in hypergraph.nodes[node]['hyperedges']:
                p = node_set & set(hyperedge)
                if len(p) >= 2:
                    subhypergraph.add_edges_from([(u, v) for u in p for v in p if u != v])
                    subhypergraph.nodes[node]['hyperedges'].append(p)
    return subhypergraph



def load_set_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        integers = content.split()
        string_set = set(map(str, integers))
    return string_set



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


