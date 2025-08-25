import networkx as nx
import time
import os
import argparse
import NPA
import EPA
import utils
import BCA
import tracemalloc
import psutil
import decomposition as decompose
import linecache
from memory_profiler import profile

parser = argparse.ArgumentParser(description="Peeling Algorithm for Hypergraph (k, g)-core")
parser.add_argument("--algorithm", help="Algorithm to use", choices=["NPA", "EPA", "BCA"], default="BCA")
parser.add_argument("--network", help="Path to the network file", default='./datasets/real/instacart/network.hyp')
parser.add_argument("--k", type=int, help="Value of k", default=3)
parser.add_argument("--g", type=int, help="Value of g", default=30000)
parser.add_argument("--parallel", action="store_true", help="Enable parallel processing for BCA algorithm")
parser.add_argument("--max_workers", type=int,
                    help="Maximum number of workers for parallel processing (default: CPU count)", default=None)
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

def main():
    args = parser.parse_args()

    # Load hypergraph
    hypergraph, E = utils.load_hypergraph(args.network)

    # Start memory tracing
    tracemalloc.start()

    result_nodes = None          # iterable of node ids
    result_map = None            # dict like {(k,g): set(nodes)}
    start_time = time.time()
    end_time = start_time

    # Algorithm execution
    if args.algorithm == "NPA":
        if args.verbose:
            print(f"Running NPA algorithm with k={args.k}, g={args.g}")
        start_time = time.time()
        G, NOM = NPA.run(hypergraph, args.k, args.g)   # G: 노드 집합이라 가정
        end_time = time.time()
        result_nodes = G
        result_map = None

    elif args.algorithm == "EPA":
        if args.verbose:
            print(f"Running EPA algorithm with k={args.k}, g={args.g}")
        start_time = time.time()
        G = EPA.run(hypergraph, args.k, args.g)        # G: 노드 집합
        end_time = time.time()
        result_nodes = G
        result_map = None

    elif args.algorithm == "BCA":
        if args.parallel:
            if args.verbose:
                print(f"Running BCA algorithm in parallel mode with max_workers={args.max_workers}")
            start_time = time.time()
            D = BCA.run_parallel_by_g(
                hypergraph,
                max_workers=args.max_workers,
                use_processes=True
            )  # D: {(k,g): set(nodes)}
            end_time = time.time()
            result_map = D
            # 모든 (k,g)-core 노드 합집합 (필요 시 다른 정책 가능)
            result_nodes = set()
            for s in D.values():
                result_nodes |= s
        else:
            if args.verbose:
                print(f"Running BCA (single) via decompose.run()")
            start_time = time.time()
            D = decompose.run(hypergraph)              # G: 노드 집합이라 가정
            end_time = time.time()
            result_map = D
            # 모든 (k,g)-core 노드 합집합 (필요 시 다른 정책 가능)
            result_nodes = set()
            for s in D.values():
                result_nodes |= s

    # Get memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Print memory usage
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    print(f"Execution time: {end_time - start_time:.2f} seconds")

    # Prepare output
    output_dir = os.path.dirname(args.network)

    # 파일명 규칙 통일
    if args.algorithm == "BCA":
        if args.parallel:
            output_filename = f"{args.algorithm}_parallel_workers_{args.max_workers}_result.dat"
        else:
            output_filename = f"{args.algorithm}_result.dat"   
    else:
        output_filename = f"{args.algorithm}_{args.k}_{args.g}_core.dat"

    output_path = os.path.join(output_dir, output_filename)

    # Write results to file
    with open(output_path, 'w') as f:
        f.write(f"Algorithm: {args.algorithm}\n")
        if args.algorithm in ("NPA", "EPA"):
            f.write(f"Parameters: k={args.k}, g={args.g}\n")
        elif args.algorithm == "BCA":
            if args.parallel:
                f.write(f"Mode: parallel (max_workers={args.max_workers if args.max_workers else 'CPU count'})\n")
            else:
                f.write(f"Mode: single\n")

        # 결과 요약
        if result_nodes is not None:
            f.write(f"Num of nodes: {len(result_nodes)}\n")

        # 성능
        f.write(f"Run Time: {end_time - start_time:.4f} seconds\n")
        f.write(f"Memory Usage(MB): {peak / 1024 / 1024:.2f} MB\n")
        f.write("=" * 50 + "\n")

        # 상세 결과
        if result_map:  # BCA 병렬: (k,g)별로 출력
            f.write("Results (k,g -> nodes):\n")
            for (k, g), nodes in sorted(result_map.items()):
                f.write(f"({k},{g}): ")
                f.write(" ".join(map(str, sorted(nodes))) + "\n")
        elif result_nodes is not None:
            f.write("Nodes: ")
            f.write(" ".join(map(str, sorted(result_nodes))) + "\n")

    print(f"Results written to {output_path}")


if __name__ == "__main__":
    main()