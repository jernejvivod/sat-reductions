import argparse
import glob
import logging
import os
import subprocess

from sat_reductions.k_clique.reduce_clique import parse_graph, find_max_k_for_graph
from sat_reductions.n_queens.reduce_nq_sat import reduce_nq_sat

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if __name__ == '__main__':

    # path to SAT solver
    SAT_SOLVER_PATH = os.path.join(os.path.dirname(__file__), 'cryptominisat/build/cryptominisat5')

    # parse arguments
    parser = argparse.ArgumentParser(prog='sat-reductions')
    subparsers = parser.add_subparsers(help='which reduction to perform', dest='reduction', required=True)
    parser_nq = subparsers.add_parser('nq', help='n-queens problem')
    parser_nq.add_argument('--n', type=int, default=4, help='the size of the chessboard (number of queens)')
    parser_nq.add_argument('--solve', action='store_true', help='solve the problem using the SAT solver and output the solution')
    parser_nq.add_argument('--solution-path', type=str, default=os.path.join(os.path.dirname(__file__), 'n_queens.solution'), help='path to the file in which to store the results')

    parser_clq = subparsers.add_parser('clq', help='k-clique problem')
    parser_clq.add_argument('--graphs-path', type=str, default=os.path.join(os.path.dirname(__file__), 'graph_data'), help='path to directory containing the graph edge lists')
    parser_clq.add_argument('--solution-path', type=str, default=os.path.join(os.path.dirname(__file__), 'max_k_for_graphs.solution'), help='path to the file in which to store the results')

    args = parser.parse_args()

    if args.reduction == 'nq':
        # perform reduction to SAT and get clauses in CNF and write to file
        res = reduce_nq_sat(args.n)
        with open(args.solution_path, 'w') as f:
            f.write(res)

        if args.solve:
            logger.info('Running SAT solver.')
            sol = subprocess.run([SAT_SOLVER_PATH, '--verb=0', args.solution_path], stdout=subprocess.PIPE)
            sat_output = sol.stdout.decode('utf8')
            logger.info('SAT solver finished running.')
            print('SAT SOLVER RESULTS:')
            print(sat_output)
            queen_pos_list = list(filter(lambda x: x.isnumeric(), sat_output.split(' ')))
            if len(queen_pos_list) > 1:
                print('Queens can be placed on positions: {0}'.format(', '.join(queen_pos_list)))

    elif args.reduction == 'clq':
        # find max k value for each graph and write results to file
        with open(args.solution_path, 'w') as f:
            for file_path in sorted(glob.glob(os.path.join(args.graphs_path, '*.graph'))):
                logger.info('computing largest clique size for graph in {0}'.format(file_path))
                nodes, adj_dict = parse_graph(file_path)
                res = find_max_k_for_graph(nodes, adj_dict, SAT_SOLVER_PATH)
                f.write('{0}: {1}\n'.format(file_path, res))
