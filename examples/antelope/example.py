"""Demonstration of automatic nonogram solution using the nonogram_solver module."""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from nonogram_solver import Nonogram

# define puzzle
top_nums = [
    [1,3],
    [2,2,1],
    [1,5],
    [3,2],
    [1,4],
    [1,1,3,3],
    [1,1,1,1],
    [1,2,2],
    [1,1,1,3],
    [1,1,1,3,1],
    [3,2,2],
    [5,1],
    [1,7],
    [2,4,2,1],
    [1,3]
    ]
side_nums = [
    [5],
    [1,5],
    [3,1],
    [2,2],
    [3,3],
    [5,4],
    [2,4,2],
    [1,1,2],
    [1,4,1],
    [4,7],
    [4,2,2],
    [2,2,2,1],
    [1,1,1,1],
    [1,1,1,1],
    [1,1,1]
    ]
my_nonogram = Nonogram(top_nums, side_nums)

# solve puzzle
my_nonogram.solve()

# plot solution
my_nonogram.plot_field()
