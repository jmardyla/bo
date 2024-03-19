import math

import numpy as np
from .model import Assignment, AssignmentProblem, NormalizedAssignmentProblem
from typing import List, Dict, Tuple, Set
from numpy.typing import ArrayLike

class Solver:
    '''
    A hungarian solver for the assignment problem.

    Methods:
    --------
    __init__(problem: AssignmentProblem):
        creates a solver instance for a specific problem
    solve() -> Assignment:
        solves the given assignment problem
    extract_mins(costs: ArrayLike):
        substracts from columns and rows in the matrix to create 0s in the matrix
    find_max_assignment(costs: ArrayLike) -> Dict[int,int]:
        finds the biggest possible assinments given 0s in the cost matrix
        result is a dictionary, where index is a worker index, value is the task index
    add_zero_by_crossing_out(costs: ArrayLike, partial_assignment: Dict[int,int])
        creates another zero(s) in the cost matrix by crossing out lines (rows/cols) with zeros in the cost matrix,
        then substracting/adding the smallest not crossed out value
    create_assignment(raw_assignment: Dict[int, int]) -> Assignment:
        creates an assignment instance based on the given dictionary assignment
    '''
    def __init__(self, problem: AssignmentProblem):
        self.problem = NormalizedAssignmentProblem.from_problem(problem)

    def solve(self) -> Assignment:
        costs = np.array(self.problem.costs)

        while True:
            self.extracts_mins(costs)
            max_assignment = self.find_max_assignment(costs)
            if len(max_assignment) == self.problem.size():
                return self.create_assignment(max_assignment)
            self.add_zero_by_crossing_out(costs, max_assignment)

    def extracts_mins(self, costs: ArrayLike):
        cost_matrix = self.problem.costs
        for i in range(cost_matrix.shape[0]):
            minimal_value = cost_matrix[i].min()
            cost_matrix[i] = cost_matrix[i] - minimal_value
        for i in range(cost_matrix.shape[1]):
            minimal_value = cost_matrix[:,i].min()
            cost_matrix[:,i] = cost_matrix[:,i] - minimal_value

    def add_zero_by_crossing_out(self, costs: ArrayLike, partial_assignment: Dict[int,int]):
        # TODO:
        # 1) "mark" columns and rows according to the instructions given by teacher
        # 2) cross out marked columns and not marked rows
        # 3) find minimal uncrossed value and subtract it from the cost matrix
        # 4) add the same value to all crossed out columns and rows
        # tip. just modify the costs matrix
        raise NotImplementedError()

    def find_max_assignment(self, costs) -> Dict[int,int]:
        partial_assignment = dict()
        # TODO: find the biggest assignment in the cost matrix
        # 1) always try first the row with the least amount of 0s
        # 2) then use column with the least amount of 0s
        # TIP: remember, rows and cols can't repeat in the assignment
        #      partial_assignment[1] = 2 means that the worker with index 1
        #                                has been assigned to task with index 2
        costs_copy = np.copy(costs)
        changed = True

        while changed:
            zeros_cords = dict()

            for i in range(costs_copy.shape[0]):
                zeros_ind = np.where(costs_copy[i] == 0)[0]
                number_of_zeros_in_row = len(zeros_ind)

                for j in zeros_ind:
                    number_of_zeros_in_column = list(costs_copy[:, j]).count(0)

                    zeros_cords[(i, j)] = (number_of_zeros_in_row, number_of_zeros_in_column)

            # min_tuple = zeros_cords[next(iter(zeros_cords))]
            # # print(min_tuple)
            # cords_tuple = next(iter(zeros_cords))
            min_tuple = (100000000, 100000000)
            cords_tuple = (100000000, 100000000)
            changed = False
            # (0, 0): (1, 1), (1, 1): (2, 1), (1, 2): (2, 2), (2, 2): (1, 2)}
            for cords, tuple1 in zeros_cords.items():
                if tuple1[0] != 0 and tuple1[0] < min_tuple[0]:

                    min_tuple = tuple1
                    cords_tuple = cords
                    changed = True

                elif tuple1[0] != 0 and tuple1[0] == min_tuple[0] and tuple1[1] != 0 and tuple1[1] < min_tuple[1]:
                    min_tuple = tuple1
                    cords_tuple = cords
                    changed = True

            if changed:
                print("Done")
                partial_assignment[int(cords_tuple[0])] = int(cords_tuple[1])
                # print(partial_assignment[cords_tuple[0]])

                costs_copy[cords_tuple[0]] = 100000000

                costs_copy[:, cords_tuple[1]] = 100000000
        print(partial_assignment)
        return partial_assignment

    def create_assignment(self, raw_assignment: Dict[int,int]) -> Assignment:
        # TODO: create an assignment instance based on the dictionary
        # tips:
        # 1) use self.problem.original_problem.costs to calculate the cost
        # 2) in case the original cost matrix (self.problem.original_problem.costs wasn't square)
        #    and there is more workers than task, you should assign -1 to workers with no task
        assignment = None
        total_cost = None
        return Assignment(assignment, total_cost)