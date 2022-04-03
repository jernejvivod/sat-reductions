# SAT Reduction Examples

This project contains several examples of reductions of well-known problems to the SAT problem. This formulation can then be Solved
using an efficient SAT colver.

Author: Jernej Vivod

## Running the Examples

To run the examples, first obtain and build the [CryptoMiniSat](https://github.com/msoos/cryptominisat) solver using the [get_sat_solver.sh](get_sat_solver.sh) script.
The implementations can then be run simply by calling `python3 sat-reductions {reduction-name}`. The list of implemented reductions can be obtained by `python3 sat-reductions --help`.

The implementations support additional arguments for the reductions (that override default values) that can be listed with the help flag for a particular reduction:
```
$ python3 sat-reductions nq --help
usage: sat-reductions nq [-h] [--n N] [--solve] [--solution-path SOLUTION_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --n N                 the size of the chessboard (number of queens)
  --solve               solve the problem using the SAT solver and output the solution
  --solution-path SOLUTION_PATH
                        path to the file in which to store the results
```

```
$ python3 sat-reductions clq --help
usage: sat-reductions clq [-h] [--graphs-path GRAPHS_PATH] [--solution-path SOLUTION_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --graphs-path GRAPHS_PATH
                        path to directory containing the graph edge lists
  --solution-path SOLUTION_PATH
                        path to the file in which to store the results

```

By default, the solutions are written in generated files in the root project directory.
