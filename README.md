# Nonogram_solver
A simple code to solve nonogram puzzles

Example of the code usage:

import Nonogram_solver
top_digits = [[1,3],[2,2,1],[1,5],[3,2],[1,4],[1,1,3,3],[1,1,1,1],[1,2,2],[1,1,1,3],[1,1,1,3,1],[3,2,2],[5,1],[1,7],[2,4,2,1],[1,3]]
side_digits = [[5],[1,5],[3,1],[2,2],[3,3],[5,4],[2,4,2],[1,1,2],[1,4,1],[4,7],[4,2,2],[2,2,2,1],[1,1,1,1],[1,1,1,1],[1,1,1]]
my_nonogram = Nonogram_solver.Nonogram(top_digits, side_digits)
my_nonogram.solve()
my_nonogram.plot_field()

Here the puzzle is defined with the lists top_digits and side_digits organized as [[column1], [column2],...] and [[row1], [row2],...] respectively. The puzzle is solved with my_nonogram.solve() and the solution is plotted with my_nonogram.plot_field().
