import itertools
import os
import subprocess

from sat_reduction_examples.k_clique import logger


def reduce_clique(nodes, adj_dict, k):
    """Get expression that formulates the k-clique problem as a SAT problem.

    :param nodes: set of unique nodes of the graph
    :param adj_dict: adjacency map mapping nodes to their neighbors
    :param k: the k parameter for the k-clique problem
    :return: expression formulating the k-clique problem as a SAT problem in DIMACS format
    """

    logger.info('reducing k-clique problem to SAT for a graph with {0} nodes and k={1}'.format(len(nodes), k))

    # initialize string for the clauses and the counter of clauses
    clauses = ''
    clauses_count = 0

    # enumerate nodes
    enumerated_nodes = {idx: n for idx, n in enumerate(nodes)}

    # build clauses for first condition (one and only one node is the i-th node in the clique)
    clauses += ''.join([' '.join(map(str, range(x, len(nodes) * k + 1, k))) + ' 0\n' for x in range(1, k + 1)])
    clauses += ''.join(['-{0} -{1} 0\n'.format(str(i), str(j)) for r in range(1, k + 1) for i in range(r, k * len(nodes), k) for j in range(i + k, k * len(nodes) + 1, k)])
    clauses_count += k
    clauses_count += len(nodes) * (len(nodes) - 1) / 2 * k  # note formula

    # build clauses for second condition (a node cannot be both the i-th and j-th node in the clique if i != j)
    clauses += ''.join(['-{0} -{1} 0\n'.format(i, j) for n in range(len(nodes)) for i in range(1 + n * k, n * k + k) for j in range(i + 1, n * k + k + 1)])
    clauses_count += k * (k - 1) / 2 * len(nodes)  # note formula

    # build clauses for third condition (if a node could be the i-th node in a clique and another node could be the j-th node in a clique
    # and if there is no edge between them, then the one of them is not in the clique)
    non_connected_pairs = [(i, j) for i in range(len(nodes) - 1) for j in range(i + 1, len(nodes)) if enumerated_nodes[j] not in adj_dict[enumerated_nodes[i]]]
    diff_r = list(itertools.permutations(range(1, k + 1), 2))  # get list of unequal indices in clique
    for pair in non_connected_pairs:
        for df in diff_r:
            exp = '-{0} -{1} 0\n'.format(str(pair[0] * k + df[0]), str(pair[1] * k + df[1]))
            clauses += exp
            clauses_count += 1

    # prepend header and return result
    return 'p cnf {0} {1}\n'.format(len(nodes) * k, int(clauses_count)) + clauses


def parse_graph(path):
    """Parse graph represented as an edge list and return a set of unique nodes in the graph and
    an adjacency map.

    :param path: path to the file containing the edge list graph definition
    :return: tuple of a set of unique nodes in the graph and an adjacency map mapping nodes to their neighbors
    """
    nodes = set()
    adj_dict = dict()
    with open(path, 'r') as f:
        for line in f:
            ln_nxt = tuple(map(int, line.strip().split(' ')))
            nodes.update(ln_nxt)
            adj_dict.setdefault(ln_nxt[0], []).append(ln_nxt[1])
            adj_dict.setdefault(ln_nxt[1], []).append(ln_nxt[0])

    return nodes, adj_dict


def find_max_k_for_graph(nodes, adj_dict):
    """Find maximum size of a clique in a graph using reduction to SAT and a SAT solver.

    :param nodes: set of unique nodes of the graph
    :param adj_dict: adjacency map mapping nodes to their neighbors
    :return: largest clique size in the graph
    """
    _TMP_SOL_PATH = os.path.join(os.path.dirname(__file__), '.clq.sol')
    _SAT_SOLVER_PATH = os.path.join(os.path.dirname(__file__), '../../cryptominisat/build/cryptominisat5')
    found = False
    k = 2
    while not found:
        clauses = reduce_clique(nodes, adj_dict, k)
        with open(_TMP_SOL_PATH, 'w') as f:
            f.write(clauses)
        sol = subprocess.run([_SAT_SOLVER_PATH, '--verb=0', _TMP_SOL_PATH], stdout=subprocess.PIPE)
        if 'UNSATISFIABLE' in sol.stdout.decode('utf8'):
            found = True
        else:
            k += 1

    os.remove(_TMP_SOL_PATH)
    return k - 1


if __name__ == '__main__':
    import argparse
    import glob

    # set path to file for storing results
    SOLUTION_PATH = os.path.join(os.path.dirname(__file__), 'max_k_for_graphs.solution')

    parser = argparse.ArgumentParser()
    parser.add_argument('--graphs-path', type=str, default=os.path.join(os.path.dirname(__file__), 'data'), help='path to directory containing the graph edge lists')
    args = parser.parse_args()

    # find max k value for each graph and write results to file
    with open(SOLUTION_PATH, 'w') as f:
        for file_path in sorted(glob.glob(os.path.join(args.graphs_path, '*.graph'))):
            logger.info('computing largest clique size for graph in {0}'.format(file_path))
            nodes, adj_dict = parse_graph(file_path)
            res = find_max_k_for_graph(nodes, adj_dict)
            f.write('{0}: {1}\n'.format(file_path, res))
