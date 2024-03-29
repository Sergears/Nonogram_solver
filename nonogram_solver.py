"""Automatic nonogram sover."""
import copy
import time
from typing import List
from math import factorial
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.ticker import MultipleLocator

# States of puzzle field
UNKNOWN = 0
SPACE = 1
PAINTED = 2

class Nonogram:
    """Solves and visualizes a nonogram puzzle.

    Example usage:
        # define puzzle
        top_nums = [[1,3],[2,2,1],...]
        side_nums = [[5],[1,5],...]
        my_nonogram = Nonogram(top_nums, side_nums)

        # solve puzzle
        my_nonogram.solve()

        # plot solution
        my_nonogram.plot_field()

    Attributes:
        top_nums (List[List[int]]): top part of the puzzle inputs
            in the form [[col1], [col2],...], e.g. [[1,3],[2,2,1],...]
        side_nums (List[List[int]]): side part of the puzzle inputs
            in the form [[row1], [row2],...], e.g. [[5],[1,5],...]
        n_rows (int): number of rows in the puzzle
        n_cols (int): number of columns in the puzzle
        field (List[List[int]]): current solution state consisting of integer 
            values UNKNOWN, SPACE, or PAINTED
        rows_skipped (List[int]): row indexes that were skipped to come back to later
        cols_skipped (List[int]): column indexes that were skipped to come back to later
    """

    def __init__(self, top_nums: List[List[int]], side_nums: List[List[int]]):
        """
        Args:
            top_nums (List[List[int]]): top part of the puzzle inputs
                in the form [[col1], [col2],...], e.g. [[1,3],[2,2,1],...]
            side_nums (List[List[int]]): side part of the puzzle inputs
                in the form [[row1], [row2],...], e.g. [[5],[1,5],...]
        """
        self.top_nums = top_nums
        self.side_nums = side_nums
        self.n_rows = len(side_nums)
        self.n_cols = len(top_nums)
        self.field = [[UNKNOWN for _ in range(self.n_cols)] for _ in range(self.n_rows)]
        self.rows_skipped: List[int] = []
        self.cols_skipped: List[int] = []

    def solve(self, skip_threshold: int = 30_000_000_000) -> None:
        """
        Public method that is called on an instance of Nonogram class
        in order to solve the puzzle. Output: populates self.field
        attribute of the class instance with the solution.

        Args:
            skip_threshold (int): threshold for number of solution options
            above which to skip the line
        """
        time_start = time.time()

        # first, find what rows and cols to skip now and solve later
        self._define_lines_to_skip(skip_threshold)

        # before doing solution passes, do fast initial painting of the field
        self._paint_block_overlaps()

        # then, do solution passes until completely solved
        self._iterate_until_solved()

        time_finish = time.time()
        print(f"elapsed time: {round(time_finish - time_start, 1)} seconds")

    def _define_lines_to_skip(self, skip_threshold: int) -> None:
        """
        Find which rows and columns to skip solving in case of too many
        options (combinations to place the blocks). Output: populates attributes
        self.rows_skipped and self.cols_skipped with indexes of the rows and
        columns to skip.

        Args:
            skip_threshold (int): threshold for number of solution options above
            which to skip the line
        """
        for ind_row in range(self.n_rows):  # go row by row
            block_lengths = self.side_nums[ind_row]
            n_options = self._estimate_n_options(block_lengths, self.n_cols)
            if n_options > skip_threshold:
                self.rows_skipped.append(ind_row)
                print(f"{n_options} options in row {ind_row} - will be skipped")
        for ind_col in range(self.n_cols):  # go column by column
            block_lengths = self.top_nums[ind_col]
            n_options = self._estimate_n_options(block_lengths, self.n_rows)
            if n_options > skip_threshold:
                self.cols_skipped.append(ind_col)
                print(f"{n_options} options in column {ind_col} - will be skipped")

    def _estimate_n_options(self, block_lengths: List[int], n_line: int) -> int:
        """
        Make an estimate of the number of possible options to solve the line.

        Args:
            block_lengths (List[int]): block lengths in the given line
            n_line (int): line length

        Returns:
            (int): number of possible options to solve the line
        """
        free_squares = n_line - sum(block_lengths)
        n_ways_last_gap_not_empty = 0
        if free_squares >= len(block_lengths):
            n_ways_last_gap_not_empty = (
                factorial(free_squares)
                // factorial(len(block_lengths))
                // factorial(free_squares - len(block_lengths))
            )
        n_ways_last_gap_empty = (
            factorial(free_squares)
            // factorial(len(block_lengths) - 1)
            // factorial(free_squares - len(block_lengths) + 1)
        )
        return n_ways_last_gap_not_empty + n_ways_last_gap_empty

    def _paint_block_overlaps(self) -> None:
        """
        Do fast initial painting of the field where a block's minimum end position
        is higher than its maximum start position. Output: updates self.field
        attribute of the class instance replacing some UNKNOWN values with PAINTED
        values.
        """
        for ind_row in range(self.n_rows):  # go row by row
            block_lengths = self.side_nums[ind_row]
            for i, _ in enumerate(block_lengths):
                min_finish = i + sum(
                    block_lengths[: i + 1]
                )  # minimum possible end of the block
                max_start = (
                    self.n_cols - sum(block_lengths[i:]) - (len(block_lengths) - i - 1)
                )  # maximum possible start of the block
                self.field[ind_row][max_start:min_finish] = [PAINTED] * (
                    min_finish - max_start
                )  # paint in between
        for ind_col in range(self.n_cols):  # go column by column
            block_lengths = self.top_nums[ind_col]
            for i in range(len(block_lengths)):
                min_finish = i + sum(
                    block_lengths[: i + 1]
                )  # minimum possible end of the block
                max_start = (
                    self.n_rows - sum(block_lengths[i:]) - (len(block_lengths) - i - 1)
                )  # maximum possible start of the block
                for ind_row in range(self.n_rows):  # paint in between
                    if max_start <= ind_row < min_finish:
                        self.field[ind_row][ind_col] = PAINTED

    def _iterate_until_solved(self):
        """
        Iteratively solve the puzzle, updating self.field on each iteration.
        """
        iteration_count = 0
        while True:
            print(f"starting iteration {iteration_count}")
            field_save = copy.deepcopy(self.field)  # save field before the iteration
            self._do_solution_iteration()
            flattened_field = [item for sublist in self.field for item in sublist]
            if UNKNOWN not in flattened_field:
                # stop if the entire field is solved
                print("puzzle is successfully solved")
                break
            if self.field == field_save:
                # if no progress was made
                if not self.rows_skipped and not self.cols_skipped:
                    # no lines skipped to come back to -> cannot solve any more
                    print(
                        f"stopping because no progress after iteration {iteration_count}"
                    )
                    break
                # progress can still be made by starting solving with skipped lines
                print("no progress - solving with the skipped rows and columns")
                self.rows_skipped = []
                self.cols_skipped = []
            iteration_count += 1

    def _do_solution_iteration(self) -> None:
        """
        Do one iteration of solving the field
        """
        self._solve_rows()
        self._solve_columns()

    def _solve_rows(self):
        """
        Go through all rows and update them one by one where progress is made.
        """
        for ind_row in range(self.n_rows):
            if ind_row in self.rows_skipped:
                print(f"\tSKIPPING row {ind_row}")
            else:
                print(f"\tsolving row {ind_row}")
                line = self.field[ind_row]
                block_lengths = self.side_nums[ind_row]
                updated_line = self._update_line(line, block_lengths)
                self.field[ind_row] = updated_line

    def _solve_columns(self):
        """
        Go through all columns and update them one by one where progress is made.
        """
        for ind_col in range(self.n_cols):
            if ind_col in self.cols_skipped:
                print(f"\tSKIPPING column {ind_col}")
            else:
                print(f"\tsolving column {ind_col}")
                line = [row[ind_col] for row in self.field]
                block_lengths = self.top_nums[ind_col]
                updated_line = self._update_line(line, block_lengths)
                for ind_row in range(self.n_rows):
                    self.field[ind_row][ind_col] = updated_line[ind_row]

    def _update_line(self, line: List[int], block_lengths: List[int]) -> List[int]:
        """
        Update a line (row or column). First, an option is constructed to
        initialize the line. Then, for each position in the line, its state
        is verified by contradiction: it is assumed that the state is the
        opposite of the initialized one, and an option is searched that
        satisfies it. If no such option exists, the state is verified.

        Args:
            line (List[int]): a line (row or column) of the current field
            block_lengths (List[int]): block lengths in the given line

        Returns:
            updated_line (List[int]): updated state of the input line
        """
        if line == [UNKNOWN] * len(line):
            # nothing was discovered at the paint_overlap step and nothing
            # has been added since, there can be no progress
            return line

        positions_to_check = [
            ind for ind, state in enumerate(line) if state == UNKNOWN
        ]  # only consider undiscovered positions
        updated_states = self._initialize_line(positions_to_check, line, block_lengths)
        for ind, position in enumerate(positions_to_check):  # go through each position
            line_to_contradict = list(line)
            if updated_states[ind] == SPACE:
                line_to_contradict[position] = PAINTED
            else:
                line_to_contradict[position] = SPACE
            if position < len(line) / 2:
                # if position is closer to the beginning, start countion options from
                # the start, otherwise from the end
                options = self._generate_option(line_to_contradict, block_lengths)
            else:
                options = self._generate_option(
                    line_to_contradict[::-1], block_lengths[::-1]
                )
            for _ in options:
                updated_states[ind] = UNKNOWN
                break
        updated_line = copy.deepcopy(
            line
        )  # construct updated line by copying the line, and changing the discovered positions
        for i, position in enumerate(positions_to_check):
            updated_line[position] = updated_states[i]
        return updated_line

    def _initialize_line(
        self, positions_to_check: List[int], line: List[int], block_lengths: List[int]
    ) -> List[int]:
        """
        A helper function to initialize line's positions with first
        possible option. If no option is found, raise an error.

        Args:
            positions_to_check (List[int]): indexes in the line we are trying to solve
            line: (List[int]): a line (row or column) of the current field
            block_lengths (List[int]): block lengths in the given line

        Returns:
            initialized_states (List[int]): initialized line's positions
        """
        initialized_states = None
        for option in self._generate_option(line, block_lengths):
            initialized_states = [option[k] for k in positions_to_check]
            break
        if initialized_states is None:
            print("CONTRADICTION FOUND, CHECK INPUT")
            raise ValueError
        return initialized_states

    def _generate_option(
        self,
        line: List[int],
        block_lengths: List[int],
        ind_block: int = 0,
        previous_block_positions: List[int] | None = None,
    ):
        """
        Generate an option - a list of states (SPACE or PAINTED) that does not contradict
        the already discovered field. It does it by placing the first block in
        all possible positions, and then calling itself recursively to place the
        next blocks. Once the final block is placed, the option is yielded.

        Args:
            line (List[int]): a line (row or column) of the current field
            block_lengths (List[int]): block lengths in the given line
            ind_block (int): the index of the first block to place (should
                be 0 unless called recursively)
            previous_block_positions (List[int]): positions of the already
                placed blocks (should be empty unless called recursively)

        Returns:
            option (List[int]): a list of states (SPACE or PAINTED) that does not
                contradict the already discovered field
        """
        if previous_block_positions is None:
            previous_block_positions = []
        if ind_block == 0:
            # if it is the first block in the line, start with 0
            min_start = 0
        else:
            # otherwise start with the end of the previous block + 1 space square
            min_start = previous_block_positions[-1] + block_lengths[ind_block - 1] + 1
        max_start = (
            len(line)
            - sum(block_lengths[ind_block:])
            - (len(block_lengths) - ind_block - 1)
        )

        for starting_position in range(min_start, max_start + 1):
            block_fits = self._find_if_block_fits(
                ind_block,
                starting_position,
                block_lengths,
                previous_block_positions,
                line,
            )
            if block_fits:
                # if the block fits in the field, add its position to the list
                # and continue recursively
                block_positions = previous_block_positions + [starting_position]
                if ind_block != len(block_lengths) - 1:
                    yield from self._generate_option(
                        line, block_lengths, ind_block + 1, block_positions
                    )
                else:
                    # once the final block is placed, convert the block positions
                    # to an option and yield
                    option = [SPACE] * len(
                        line
                    )  # start with all spaces, then paint where needed
                    for i_block, block_position in enumerate(block_positions):
                        option[
                            block_position : block_position + block_lengths[i_block]
                        ] = [PAINTED] * block_lengths[i_block]
                    yield option

    def _find_if_block_fits(
        self,
        ind_block: int,
        starting_position: int,
        block_lengths: List[int],
        previous_block_positions: List[int],
        line: List[int],
    ) -> bool:
        """
        Check if the block fits within the already discovered field.

        Args:
            ind_block (int): the index of the first block to place (should
                be 0 unless called recursively)
            starting_position (int): minimum starting position of the block
            block_lengths (List[int]): block lengths in the given line
            previous_block_positions (List[int]): positions of the already
                placed blocks (should be empty unless called recursively)
            line (List[int]): a line (row or column) of the current field

        Returns:
            (bool): True if the block fits in the line, False otherwise
        """
        if SPACE in line[starting_position : starting_position + block_lengths[ind_block]]:
            return (
                False  # block does not fit if there must be spaces where it's painted
            )

        if ind_block == 0:
            # if it's the first block in the line, there must be spaces starting from 0
            space_start = 0
        else:
            # otherwise, there must be spaces starting from the end of the previous block
            space_start = previous_block_positions[-1] + block_lengths[ind_block - 1]
        if PAINTED in line[space_start:starting_position]:
            # block does not fit if there must be painted squares where the spaces
            # are suggested
            return False

        if ind_block == len(block_lengths) - 1:
            # if it's the last block in the line, it also implies spaces everywhere after
            if PAINTED in line[starting_position + block_lengths[ind_block] : len(line)]:
                # block does not fit if there must be painted squares where the
                # spaces are suggested
                return False
        return True

    def plot_field(self, pause: float = 0) -> None:
        """
        Plot the solved field.

        Args:
            pause (float): time to pause (in seconds) if the function
                is called after each iteration
        """
        cmap = colors.ListedColormap(["white", "blue"])
        bounds = [0, 1.5, 2]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        _, ax = plt.subplots()
        ax.imshow(
            self.field, cmap=cmap, norm=norm, extent=[0, self.n_cols, self.n_rows, 0]
        )
        for ind_row in range(self.n_rows):
            string = ""
            for digit in self.side_nums[ind_row]:
                string += str(digit) + " "
            ax.text(0, ind_row + 0.5, string, ha="right", va="center", fontsize=7)
        plt.subplots_adjust(left=0.2)
        for ind_col in range(self.n_cols):
            string = ""
            for digit in self.top_nums[ind_col]:
                string += str(digit) + "\n"
            ax.text(ind_col + 0.5, 0, string, ha="center", va="bottom", fontsize=7)
        plt.subplots_adjust(top=0.8)
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.yaxis.set_minor_locator(MultipleLocator(1))
        ax.yaxis.tick_right()
        ax.grid(True, which="minor", color="k", linestyle="-", linewidth=0.25)
        ax.grid(which="major", color="k", linestyle="-", linewidth=1)
        if not pause:
            plt.show()
        else:
            plt.show(block=False)
            plt.pause(pause)
            plt.close()
