import networkx as nx
import time
import os
import argparse
import NPA
import EPA
import utils
import decomposition
import tracemalloc
# import psutil
import linecache

def display_top(snapshot, key_type='lineno', limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    total = sum(stat.size for stat in top_stats) # stat.size -> Bytes
    return total

parser = argparse.ArgumentParser(description="Peeling Algorithm for Hypergraph (k, g)-core")
parser.add_argument("--algorithm", help="Algorithm to use", choices=["NPA", "EPA", "decom"], default="NPA")
parser.add_argument("--network", help="Path to the network file"
                    ,default='./datasets/real/contact/network.hyp')
parser.add_argument("--k", type=int, help="Value of k",default=3)
parser.add_argument("--g", type=int, help="Value of g",default=3)
args = parser.parse_args()

tracemalloc.start()
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

snapshot = tracemalloc.take_snapshot()
memory_usage = display_top(snapshot)



# Write results to file
output_dir = os.path.dirname(args.network)

if args.algorithm == "decom":
    output_filename = f"decomposition.dat"
else:
    output_filename = f"{args.algorithm}_{args.k}_{args.g}_core_memory.dat"
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
        output_file.write("Nodes:")
        nodes = " ".join(str(node) for node in G)
        output_file.write(nodes + "\n")

    #write memory usage
    output_file.write("Memory Usage(KB): ")
    memory = memory_usage / 1000  # bytes to KB
    output_file.write(f"{memory}\n")


print(f"Results written to {output_path}")