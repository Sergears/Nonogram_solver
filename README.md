# Nonogram_solver
A simple code to solve nonogram puzzles

Example of the code usage:

```
import Nonogram_solver
top_digits = [[1], [4], [3], [3], [1]]
side_digits = [[1], [2,2], [3], [3], [1]]
my_nonogram = Nonogram_solver.Nonogram(top_digits, side_digits)
my_nonogram.solve()
my_nonogram.plot_field()
```
Here the puzzle is defined with the lists top_digits and side_digits organized as [[column1], [column2],...] and [[row1], [row2],...] respectively. The puzzle is solved with my_nonogram.solve() and the solution is plotted with my_nonogram.plot_field().
