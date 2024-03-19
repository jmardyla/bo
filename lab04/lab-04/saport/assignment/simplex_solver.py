import numpy as np
from .model import AssignmentProblem, Assignment, NormalizedAssignmentProblem
from ..simplex.model import Model
from ..simplex.expressions.expression import Expression
from dataclasses import dataclass
from typing import List 



class Solver:
    '''
    A simplex solver for the assignment problem.

    Methods:
    --------
    __init__(problem: AssignmentProblem):
        creates a solver instance for a specific problem
    solve() -> Assignment:
        solves the given assignment problem
    '''
    def __init__(self, problem: AssignmentProblem):
        self.problem = NormalizedAssignmentProblem.from_problem(problem)

    def solve(self) -> Assignment:
        model = Model("assignment")
        # TODO:
        # 1) creates variables, one for each cost in the cost matrix
        # 2) add constraint, that sum of every row has to be equal 1
        # 3) add constraint, that sum of every col has to be equal 1
        # 4) add constraint, that every variable has to be <= 1
        # 5) create an objective expression, involving all variables weighted by their cost
        # 6) add the objective to model (minimize it!)
        #
        #  tip. model.add_constraint(Expression.from_vectors([x1,x2,x3], [3,2,1]) < 3))
        #       accepts lists as arguments and gives the same result as:
        #       model.add_constraint(3*x1 + 2*x2 + x3 < 3)

        costs_arr = np.copy(self.problem.costs)
        variable_array = []

        for i in range(costs_arr.shape[0]):
            row_list = []
            for j in range(costs_arr.shape[1]):
                var = model.create_variable("x" + str(i) + str(j))
                # variable_array[i][j] = var
                row_list.append(var)
                # "x" + str(i) + str(j)
                model.add_constraint(var <= 1)
            variable_array.append(row_list)

        variable_array = np.array(variable_array)
        for i in range(costs_arr.shape[0]):
            # model.add_constraint(Expression.from_vectors(variable_array[i, :], costs_arr[i, :]) == 1)
            model.add_constraint(Expression.from_vectors(variable_array[i, :], np.ones(costs_arr.shape[1])) == 1)
            # print(variable_array[i, :])
            # print()
            # print(costs_arr[i, :])
            # print()

        for i in range(costs_arr.shape[1]):
            # model.add_constraint(Expression.from_vectors(variable_array[:, i], costs_arr[:, i]) == 1)

            model.add_constraint(Expression.from_vectors(variable_array[:, i], np.ones(costs_arr.shape[0])) == 1)

        cost_list = [item for sublist in costs_arr for item in sublist]

        variable_list = [item for sublist in variable_array for item in sublist]

        model.minimize(Expression.from_vectors(variable_list, cost_list))

        solution = model.solve()

        # TODO:
        # 1) extract assignment for the original problem from the solution object
        # tips:
        # - remember that in the original problem n_workers() not alwyas equals n_tasks()
        workers_array = []
        sol_list = solution.assignment()
        number_of_tasks = self.problem.original_problem.n_tasks()
        number_of_workers = self.problem.original_problem.n_workers()

        for i in range(number_of_workers * costs_arr.shape[1]):
            if sol_list[i] == 1:
                task_index = i % (costs_arr.shape[1])
                if task_index > number_of_tasks-1:
                    workers_array.append(-1)
                else:
                    workers_array.append(task_index)

        assigned_tasks = workers_array
        if self.problem.original_problem.objective_is_min:
            org_objective = solution.objective_value()
        else:
            costs = np.copy(self.problem.original_problem.costs)
            shape_tuple = np.shape(costs)
            min_dimension = min(shape_tuple)
            difference_of_dimension = np.subtract(shape_tuple, (min_dimension, min_dimension))
            if difference_of_dimension[0] == 0:
                for i in range(difference_of_dimension[1]):
                    costs = np.append(costs, np.zeros((1, shape_tuple[1])), axis=0)
            else:
                for i in range(difference_of_dimension[0]):
                    costs = np.append(costs, np.zeros((shape_tuple[0], 1)), axis=1)

            cost_list = [item for sublist in costs for item in sublist]
            result = []
            for x, y in zip(cost_list, solution.assignment()):
                result.append(x * y)
            org_objective = sum(result)

        return Assignment(assigned_tasks, org_objective)