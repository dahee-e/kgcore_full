import itertools
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
import networkx as nx


_HYP = None

def _init_hypergraph(h):
    global _HYP
    _HYP = h

def run_for_g_with_global(g):
    return run_for_g(_HYP, g)


def getNbrMap(hypergraph, v, g):
    neighbor_counts = {}
    for hyperedge in hypergraph.nodes[v]['hyperedges']:
        for neighbor in hyperedge:
            if neighbor != v:
                neighbor_counts[neighbor] = neighbor_counts.get(neighbor, 0) + 1
    return {nbr: c for nbr, c in neighbor_counts.items() if c >= g}

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

def run_for_g(hypergraph, g):
    Dg = {}
    k = 0
    VQ = deque()
    queued = set()
    prev = set(hypergraph.nodes())
    C = {}
    T = defaultdict(set)
    H = set(hypergraph.nodes())

    for v in hypergraph.nodes():
        nbr_map = getNbrMap(hypergraph, v, g)
        C[v] = len(nbr_map)
        T[C[v]].add(v)

    total_nodes = {node for count, nodes in T.items() if count != 0 for node in nodes}
    if not total_nodes:
        return g, {}, True

    while H:
        k += 1
        for count_val in sorted(list(T.keys())):
            if count_val >= k:
                break
            for node in list(T[count_val]):
                if node not in queued:
                    VQ.append(node)
                    queued.add(node)
            T[count_val].clear()

        while VQ:
            current = VQ.popleft()
            queued.discard(current)
            if current not in H:
                continue
            H.remove(current)
            del C[current]

            nbr_current = [w for w in getNbrMap(hypergraph, current, g) if w in C]
            for w in nbr_current:
                if w in queued:
                    continue
                old_count = C[w]
                if w in T[old_count]:
                    T[old_count].remove(w)
                C[w] = old_count - 1
                new_count = C[w]
                T[new_count].add(w)
                if new_count < k and w not in queued:
                    VQ.append(w)
                    queued.add(w)

        if k > 1:
            Dg[(k - 1, g)] = prev - H
        prev = H.copy()

    return g, Dg, False

def num_hyperedges(hypergraph):
    seen = set()
    for v in hypergraph.nodes():
        for he in hypergraph.nodes[v].get('hyperedges', []):
            seen.add(frozenset(he))
    return len(seen)

def run_parallel_by_g(hypergraph, max_workers=None, use_processes=True):
    E = num_hyperedges(hypergraph)
    if E == 0:
        return {}

    Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    D_all = {}
    next_g_to_submit = 1
    next_g_to_consume = 1
    futures = {}
    stop_at_g = None

    if use_processes:
        ex = Executor(max_workers=max_workers, initializer=_init_hypergraph, initargs=(hypergraph,))
        submit_fn = lambda g: ex.submit(run_for_g_with_global, g)
    else:
        ex = Executor(max_workers=max_workers)
        submit_fn = lambda g: ex.submit(run_for_g, hypergraph, g)

    with ex:
        initial = min(E, max_workers or 1)
        for g in range(1, initial + 1):
            futures[submit_fn(g)] = g
            next_g_to_submit = g + 1

        while futures:
            for fut in as_completed(list(futures.keys())):
                g_done = futures.pop(fut)
                try:
                    g_ret, Dg, is_empty = fut.result()
                except Exception:
                    continue
                D_all[g_ret] = (Dg, is_empty)

                while next_g_to_consume in D_all:
                    Dg2, empty2 = D_all[next_g_to_consume]
                    if empty2:
                        stop_at_g = next_g_to_consume
                        futures.clear()
                        break
                    for k_g, Vset in Dg2.items():
                        if Vset:
                            D_all.setdefault('merged', {})[k_g] = (
                                Vset if k_g not in D_all.get('merged', {})
                                else D_all['merged'][k_g] | Vset
                            )
                    next_g_to_consume += 1

                if stop_at_g is not None:
                    break

                if stop_at_g is None and next_g_to_submit <= E:
                    futures[submit_fn(next_g_to_submit)] = next_g_to_submit
                    next_g_to_submit += 1

            if stop_at_g is not None:
                break

    merged = D_all.get('merged', {})
    return reorganise(merged)