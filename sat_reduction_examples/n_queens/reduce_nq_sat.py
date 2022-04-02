from sat_reduction_examples.n_queens import logger


def reduce_nq_sat(n):
    """Reduce the N queens problem to a SAT problem.

    Author: Jernej Vivod

    :param n: the size of the chessboard (number of queens)
    :return: the CNF problem formulation in DIMACS format
    """

    logger.info('Computing reduction of the n-Queens problem to SAT for n={0}.'.format(n))

    # initialize string for result
    clauses = ''

    # initialize counter of clauses
    clauses_count = 0

    # build clauses for rows
    logger.info('building clauses for rows')
    for idx_row in range(n):
        cl_to_add = ' '.join(map(str, range(1 + n * idx_row, (idx_row + 1) * n + 1)))
        logger.info('adding clause: {0}'.format(cl_to_add))
        clauses += cl_to_add + ' 0 \n'
        for el in [(i, j) for i in range(idx_row * n + 1, (idx_row + 1) * n) for j in range(i + 1, (idx_row + 1) * n + 1)]:
            cl_to_add = ' '.join(map(lambda x: str(-x), el))
            logger.info('adding clause: {0}'.format(cl_to_add))
            clauses += cl_to_add + ' 0 \n'
            clauses_count += 1
        clauses += ' '.join(map(str, [el for el in range(idx_row * n + 1, (idx_row + 1) * n + 1)])) + ' 0 \n'
        clauses_count += 1

    # build clauses for columns
    logger.info('building clauses for columns')
    for idx_col in range(n):
        cl_to_add = ' '.join(map(str, range(idx_col + 1, n * n - (n - 1) + idx_col + 1, n)))
        logger.info('adding clause: {0}'.format(cl_to_add))
        clauses += cl_to_add + ' 0 \n'
        for el in [(i, j) for i in range(idx_col + 1, (n - 1) * n + 1 + idx_col, n) for j in range(i + n, (n - 1) * n + 1 + 1 + idx_col, n)]:
            cl_to_add = ' '.join(map(lambda x: str(-x), el))
            logger.info('adding clause: {0}'.format(cl_to_add))
            clauses += cl_to_add + ' 0 \n'
            clauses_count += 1
        clauses += ' '.join(map(str, [el for el in range(idx_col + 1, (n - 1) * n + 1 + 1 + idx_col, n)])) + ' 0 \n'
        clauses_count += 1

    # starting indices for falling diagonals
    f_diag_start1 = list(range(1 + (n - 2) * n, 0, -n))
    f_diag_start2 = list(range(n - 1, 1, -1))

    def get_clauses_falling_diagonals(cl, cl_count, f_diag_start):
        """Compute clauses for falling diagonals.
        """
        for idx_f_diag in range(1, len(f_diag_start) + 1):
            for el in [(i, j) for i in range(f_diag_start[idx_f_diag - 1], f_diag_start[idx_f_diag - 1] + idx_f_diag * (n + 1), n + 1)
                       for j in range(i + (n + 1), f_diag_start[idx_f_diag - 1] + idx_f_diag * (n + 1) + 1, n + 1)]:
                cl_to_add = ' '.join(map(lambda x: str(-x), el))
                logger.info('adding clause: {0}'.format(cl_to_add))
                cl += cl_to_add + ' 0 \n'
                cl_count += 1

        return cl, cl_count

    def get_clauses_rising_diagonals(cl, cl_count, r_diag_start):
        """Compute clauses for rising diagonals.
        """
        for idx_r_diag in range(1, len(r_diag_start) + 1):
            for el in [(i, j) for i in range(r_diag_start[idx_r_diag - 1], r_diag_start[idx_r_diag - 1] + idx_r_diag * (n - 1), n - 1)
                       for j in range(i + (n - 1), r_diag_start[idx_r_diag - 1] + idx_r_diag * (n - 1) + 1, n - 1)]:
                cl_to_add = ' '.join(map(lambda x: str(-x), el))
                logger.info('adding clause: {0}'.format(cl_to_add))
                cl += cl_to_add + ' 0 \n'
                cl_count += 1

        return cl, cl_count

    # build clauses for falling diagonals
    logger.info('building clauses for falling diagonals.')
    clauses, clauses_count = get_clauses_falling_diagonals(clauses, clauses_count, f_diag_start1)
    clauses, clauses_count = get_clauses_falling_diagonals(clauses, clauses_count, f_diag_start2)

    # starting indices for rising diagonals
    r_diag_start1 = list(range(2, n + 1))
    r_diag_start2 = list(range(n * (n - 1), 2 * n - 1, -n))

    # build clauses for rising diagonals
    logger.info('building clauses for rising diagonals')
    clauses, clauses_count = get_clauses_rising_diagonals(clauses, clauses_count, r_diag_start1)
    clauses, clauses_count = get_clauses_rising_diagonals(clauses, clauses_count, r_diag_start2)

    # prepend header and return result
    return 'p cnf {0} {1}\n'.format(n * n, clauses_count) + clauses


if __name__ == '__main__':
    import os
    import argparse
    import subprocess

    # path to output file
    RESULTS_FILE_PATH = 'nq.cnf'

    # path to SAT solver
    SAT_SOLVER_PATH = os.path.join(os.path.dirname(__file__), '../../cryptominisat/build/cryptominisat5')

    # parse the size of the chessboard (number of queens)
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=4, help="the size of the chessboard (number of queens)")
    parser.add_argument('--solve', action='store_true')
    args = parser.parse_args()

    # perform reduction to SAT and get clauses in CNF and write to file
    res = reduce_nq_sat(args.n)
    with open(RESULTS_FILE_PATH, 'w') as f:
        f.write(res)

    if args.solve:
        logger.info('Running SAT solver.')
        sol = subprocess.run([SAT_SOLVER_PATH, '--verb=0', RESULTS_FILE_PATH], stdout=subprocess.PIPE)
        sat_output = sol.stdout.decode('utf8')
        logger.info('SAT solver finished running.')
        print("SAT SOLVER RESULTS:")
        print(sat_output)
        queen_pos_list = list(filter(lambda x: x.isnumeric(), sat_output.split(' ')))
        if len(queen_pos_list) > 1:
            print('Queens can be placed on positions: {0}'.format(', '.join(queen_pos_list)))
