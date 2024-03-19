from ..solver import Solver
from ..model import Solution, Item
import numpy as np
from typing import List



class DynamicSolver(Solver):
    """
    A naive dynamic programming solver for the knapsack problem.
    """

    def _create_table(self) -> np.ndarray:
        # TODO: fill the table!
        # tip 1. init table using np.zeros function (replace `None``)
        # tip 2. remember to handle timeout (refer to the dfs solver for an example)
        #        - just return the current state of the table

        table = np.zeros((self.problem.capacity+1, len(self.problem.items)+1))
        list_of_items = sorted(self.problem.items, key=lambda x: x.index)
        list_of_items.insert(0, Item(0, 0, 0))

        for n in range(table.shape[1]):
            for c in range(table.shape[0]):
                if n == 0 or c == 0:
                    table[c][n] = 0
                elif list_of_items[n].weight <= c:
                    table[c][n] = max(list_of_items[n].value + table[c-list_of_items[n].weight][n-1], table[c][n-1])
                else:
                    table[c][n] = table[c][n-1]

        return table

    def _extract_solution(self, table: np.ndarray) -> Solution:
        used_items: List[Item] = []
        optimal = table[-1, -1] > 0

        # TODO: fill in the `used_items` list using info from the table!

        list_of_items = sorted(self.problem.items, key=lambda x: x.index)
        #check
        list_of_items.insert(0, Item(0, 0, 0))

        capacity_index = self.problem.capacity
        number_of_items = len(self.problem.items)

        for i in range(table.shape[1]):

            if table[capacity_index][number_of_items] != table[capacity_index][number_of_items-1]:
                if number_of_items == 0:
                    continue
                used_items.append(list_of_items[number_of_items])
                capacity_index -= list_of_items[number_of_items].weight

            number_of_items -= 1


        return Solution.from_items(used_items, optimal)

    def solve(self) -> Solution:
        self.interrupted = False
        self.start_timer()

        table = self._create_table()
        solution = self._extract_solution(table) if table is not None else Solution.empty()

        self.stop_timer()
        return solution
