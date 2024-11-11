import networkx as nx

def load_hypergraph(file_path):
    hypergraph = nx.Graph()  # Create an empty hypergraph
    E = list()

    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            nodes = line.strip().split(',')
            hyperedge = set(nodes)  # Use frozenset to represent the hyperedge
            #hypergraph.add_node(hyperedge, nodes=set())  # Add a node for the hyperedge
            E.append(hyperedge)
            for node in nodes:
                if node not in hypergraph.nodes() :
                    hypergraph.add_node(node, hyperedges=list())  # Add a node for each node
                hypergraph.nodes[node]['hyperedges'].append(hyperedge)  # Add the hyperedge to the node's hyperedge set

    return hypergraph, E


def degree(hypergraph, node):
    neighbors = set()
    for hyperedge in hypergraph.nodes[node]['hyperedges']:
        neighbors.update(hyperedge - {node})  # Collect all nodes in the hyperedge except the current node
    return len(neighbors)


# Usage example
input_file = './datasets/real/MAG/network.hyp'
hypergraph, E = load_hypergraph(input_file)

print(len(hypergraph.nodes()))
print(len(E))

sum = 0
for e in E:
    sum = sum+ len(e)

print(sum / len(E))

sum = 0
for v in hypergraph.nodes():
    sum = sum + degree(hypergraph, v)

print(sum / len(hypergraph.nodes()))