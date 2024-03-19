from ..model import Problem, Solution, Item
from typing import List
from ..solver import Solver


class BnbDFSSolver(Solver):
    """
    A branch-and-bound solver for the Knapsack Problem, 
    explores the search tree using a basic DFS strategy.
    
    Methods:
    --------
    _upper_bound(left : List[Item], solution: Solution) -> float:
        given the list of still available items and the current solution,
        calculates the linear relaxation of the problem
    """
    def dfs_bnb(self):
        self.best_solution = Solution.empty()
        return self._dfs_bnb(self.problem.items, self.best_solution)

    def _dfs_bnb(self, left: List[Item], solution: Solution):
        # TODO: implement a dfs branch-and-bound solver
        #
        #   tip 1. use the DFS code as your starting point (dfs.py)
        #   tip 2. use the _upper_bound method to calculate the upper bound
        #   tip 3. if the upper bound is lower than the current best solution, just
        #          ignore rest of the branch (a simple "return" is enough)
        if len(left) == 0:
            if solution.value > self.best_solution.value:
                self.best_solution = solution
            return

        if self.best_solution.value > self._upper_bound(left, solution):
            return

        if self.timeout():
            self.interrupted = True
            return

        space_left = self.problem.capacity - solution.weight
        item = left[0]
        new_left = left[1:]
        if item.weight <= space_left:
            self._dfs_bnb(new_left, solution.with_added_item(item))
        self._dfs_bnb(new_left, solution)


    def _upper_bound(self, left: List[Item], solution: Solution) -> float:
        # TODO: implement the linear relaxation, i.e. assume you can take
        #      fraction of the items in the backpack
        #      return the value of such a solution
        #      tip 1. solution is your "starting point" (items already in the backpack)
        #      tip 2. left is the list of items you can still take
        #      tip 3. take the items with highest value density first (as in greedy_density approach)

        our_list = sorted(left, key=lambda x: (float(x.value)/x.weight), reverse=True)
        result = float(solution.value)

        left_capacity = float(self.problem.capacity) - float(solution.weight)

        for item in our_list:
            if item.weight > left_capacity != 0:
                result += (float(left_capacity)/float(item.weight))*float(item.value)
                break
            elif left_capacity == 0:
                break
            elif item.weight <= left_capacity:
                result += float(item.value)
                left_capacity -= float(item.weight)

        return result

    def solve(self) -> Solution:
        self.interrupted = False
        self.start_timer()
        self.dfs_bnb()
        self.best_solution.optimal = not self.interrupted
        self.stop_timer()
        return self.best_solution