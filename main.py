import networkx as nx
import time
import os
import argparse
import NPA
import EPA
import utils
import decomposition




parser = argparse.ArgumentParser(description="Peeling Algorithm for Hypergraph (k, g)-core")
parser.add_argument("--algorithm", help="Algorithm to use")
parser.add_argument("--network", help="Path to the network file",default='./datasets/real/contact/network.hyp')
parser.add_argument("--k", type=int, help="Value of k")
parser.add_argument("--g", type=int, help="Value of g")
args = parser.parse_args()

# Load hypergraph
hypergraph, E = utils.load_hypergraph(args.network)

if args.algorithm == "NPA":
    start_time = time.time()
    G = NPA.run(hypergraph, args.k, args.g)
    end_time = time.time()
elif args.algorithm == "EPA":
    start_time = time.time()
    G = EPA.run(hypergraph, args.k, args.g)
    end_time = time.time()
elif args.algorithm == "decom":
    start_time = time.time()
    G = decomposition.run(hypergraph)
    end_time = time.time()
# Write results to file
output_dir = os.path.dirname(args.network)

if args.algorithm == "decom":
    output_filename = f"decomposition.dat"
else:
    output_filename = f"{args.algorithm}_{args.k}_{args.g}_core.dat"
output_path = os.path.join(output_dir, output_filename)

with open(output_path, 'w') as output_file:
    # Write size of nodes
    if args.algorithm != "decom":
        output_file.write(f"Num of nodes: {str(len(G))}\n")
    # Write running time
    output_file.write(f"Run Time: {end_time - start_time}\n")
    # Write nodes
    if args.algorithm == "decom":
        output_file.write("Result\n")
        for key, value in G.items():
            output_file.write(f"{key}: {value}\n")

    else:
        output_file.write("Nodes:\n")
        nodes = " ".join(str(node) for node in G)
        output_file.write(nodes + "\n")

print(f"Results written to {output_path}")