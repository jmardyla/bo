from collections import Counter
import numpy as np
from saport.assignment.model import Assignment, AssignmentProblem, NormalizedAssignmentProblem
from saport.assignment.hungarian_solver import Solver
from tests.common_test_utils import indented_string
import pytest

class TestHungarianSolver:

    @pytest.mark.parametrize("costs, expected_costs", [
        ([[4, 9, 8], [6, 7, 5], [4, 6, 1]], [[0, 3, 4], [1, 0, 0], [3, 3, 0]]),
        ([[2, 11, 2, 6], [3, 10, 9, 4], [8, 6, 6, 6], [10, 13, 15, 13]], [[0, 9, 0, 4], [0, 7, 6, 1], [2, 0, 0, 0], [0, 3, 5, 3]]),
        ([[2, 11, 2, 1], [3, 10, 3, 4], [8, 6, 6, 2], [11, 13, 15, 13]], [[1, 8, 1, 0], [0, 5, 0, 1], [6, 2, 4, 0], [0, 0, 4, 2]]),
        ([[4, 9, 8], [6, 7, 5], [4, 6, 9]], [[0, 3, 4], [1, 0, 0], [0, 0, 5]]),
        ([[4, 3, 8, 0], [6, 7, 5, 0], [4, 6, 9, 0], [5, 7, 4, 0]], [[0, 0, 4, 0], [2, 4, 1, 0], [0, 3, 5, 0], [1, 4, 0, 0]]),
        ([[4, 9, 8, 0], [6, 7, 5, 0], [4, 6, 9, 0], [5, 7, 4, 0]], [[0, 3, 4, 0], [2, 1, 1, 0], [0, 0, 5, 0], [1, 1, 0, 0]]),
        ([[4, 9, 8, 5], [6, 7, 5, 8], [4, 6, 9, 6], [0, 0, 0, 0]], [[0, 5, 4, 1], [1, 2, 0, 3], [0, 2, 5, 2], [0, 0, 0, 0]]),
        ([[4, 9, 8, 5], [6, 7, 5, 8], [4, 6, 1, 6], [0, 0, 0, 0]], [[0, 5, 4, 1], [1, 2, 0, 3], [3, 5, 0, 5], [0, 0, 0, 0]]),
        ([[13, 4, 13, 9], [12, 5, 6, 11], [7, 9, 9, 9], [5, 2, 0, 2]], [[9, 0, 9, 3], [7, 0, 1, 4], [0, 2, 2, 0], [5, 2, 0, 0]]),
        ([[16, 7, 16, 12], [15, 8, 9, 14], [10, 12, 12, 12], [0, 5, 3, 5]], [[9, 0, 8, 3], [7, 0, 0, 4], [0, 2, 1, 0], [0, 5, 2, 3]]),
        ([[5, 0, 1, 0], [3, 2, 4, 0], [5, 3, 0, 0], [4, 2, 5, 0]], [[2, 0, 1, 0], [0, 2, 4, 0], [2, 3, 0, 0], [1, 2, 5, 0]]),
        ([[5, 2, 1, 0], [3, 2, 4, 0], [5, 3, 0, 0], [4, 2, 5, 0]], [[2, 0, 1, 0], [0, 0, 4, 0], [2, 1, 0, 0], [1, 0, 5, 0]])
    ])
    def test_should_subtract_min_values_in_every_row_and_column_in_cost_matrix(
        self, costs, expected_costs
    ):
        cost_matrix = np.array(costs)
        problem = AssignmentProblem("test_model", cost_matrix, True)
        norm_problem = NormalizedAssignmentProblem(np.copy(cost_matrix), problem)

        solver = Solver.__new__(Solver)
        solver.problem = norm_problem

        solver.extracts_mins(solver.problem.costs)

        assert np.array_equal(
            solver.problem.costs, expected_costs
        ), "min values are not extracted properly:" +\
            f"\n- got cost matrix: {indented_string(str(solver.problem.costs))}" +\
            f"\n- expected: {indented_string(str(expected_costs))}" +\
            f"\n- from initial cost matrix: {indented_string(str(problem.costs))}"


    @pytest.mark.parametrize("costs, expected_assignment_size", [
        ([[0, 3, 4], [1, 0, 0], [3, 3, 0]], 3),
        ([[0, 9, 0, 4], [0, 7, 6, 1], [2, 0, 0, 0], [0, 3, 5, 3]], 3),
        ([[1, 8, 1, 0], [0, 5, 0, 1], [6, 2, 4, 0], [0, 0, 4, 2]], 3),
        ([[0, 3, 4], [1, 0, 0], [0, 0, 5]], 3),
        ([[0, 0, 4, 0], [2, 4, 1, 0], [0, 3, 5, 0], [1, 4, 0, 0]], 4),
        ([[0, 3, 4, 0], [2, 1, 1, 0], [0, 0, 5, 0], [1, 1, 0, 0]], 4),
        ([[0, 5, 4, 1], [1, 2, 0, 3], [0, 2, 5, 2], [0, 0, 0, 0]], 3),
        ([[0, 5, 4, 1], [1, 2, 0, 3], [3, 5, 0, 5], [0, 0, 0, 0]], 3),
        ([[9, 0, 9, 3], [7, 0, 1, 4], [0, 2, 2, 0], [5, 2, 0, 0]], 3),
        ([[9, 0, 8, 3], [7, 0, 0, 4], [0, 2, 1, 0], [0, 5, 2, 3]], 4),
        ([[2, 0, 1, 0], [0, 2, 4, 0], [2, 3, 0, 0], [1, 2, 5, 0]], 4),
        ([[2, 0, 1, 0], [0, 0, 4, 0], [2, 1, 0, 0], [1, 0, 5, 0]], 4)
    ])
    def test_should_find_partial_assignment_in_cost_matrix(
        self, costs, expected_assignment_size
    ):
        cost_matrix = np.array(costs)
        problem = AssignmentProblem("test_model", cost_matrix, True)
        norm_problem = NormalizedAssignmentProblem(np.copy(cost_matrix), problem)

        solver = Solver.__new__(Solver)
        solver.problem = norm_problem
        got_max_assignment = solver.find_max_assignment(solver.problem.costs)

        header = f"partial assignment is incorrect:" +\
                    f"\n- got: {got_max_assignment}"
        footer = f"\n- for cost matrix: {indented_string(str(cost_matrix))}"

        assert isinstance(got_max_assignment, dict), header +\
            f"\n- expected a dictionary" +\
            footer
        
        n = cost_matrix.shape[0]
        bad_keys = { key for key in got_max_assignment if not isinstance(key, int) }
        assert len(bad_keys) == 0, header +\
            f"\n- some keys ({bad_keys}) in the assignment dictionary are not of the type `int`" +\
            footer

        bad_keys = { key for key in got_max_assignment if key < 0 or key >= n }
        assert len(bad_keys) == 0, header +\
            f"\n- some keys ({bad_keys}) in the assignment dictionary do not correspond to any row in the cost matrix" +\
            footer
        
        bad_values = { val for val in got_max_assignment.values() if not isinstance(val, int) }
        assert len(bad_values) == 0, header +\
            f"\n- some values ({bad_values}) in the assignment dictionary are not of the type `int`" +\
            footer
        
        bad_values = { val for val in got_max_assignment.values() if val < 0 or val >= n }
        assert len(bad_values) == 0, header +\
            f"\n- some values ({bad_values}) in the assignment dictionary do not correspond to any column in the cost matrix" +\
            footer
        
        col_counter = Counter(got_max_assignment.values())
        duplicate_values = { k for k,v in col_counter.items() if v > 1}
        assert len(duplicate_values) == 0, header +\
            f"\n- some tasks ({duplicate_values}) are assigned more than once in the assignment" +\
            footer
        
        non_zeros = { r for (r,c) in got_max_assignment.items() if cost_matrix[r,c] > 0 }
        assert len(non_zeros) == 0, header +\
            f"\n- some workers ({non_zeros}) have been assigned to tasks with cost higher than 0" +\
            footer
        
        assert len(got_max_assignment) == expected_assignment_size, header +\
            f"\n- got assignment for only {len(got_max_assignment)} workers, expected to assign tasks to {expected_assignment_size} workers" +\
            footer


    @pytest.mark.parametrize("start_costs, partial_assignment, exp_costs", [
        ([[0, 9, 0, 4], [0, 7, 6, 1], [2, 0, 0, 0], [0, 3, 5, 3]], {1: 0, 0: 2, 2: 1}, [[1, 9, 0, 4], [0, 6, 5, 0], [3, 0, 0, 0], [0, 2, 4, 2]]),
        ([[1, 8, 1, 0], [0, 5, 0, 1], [6, 2, 4, 0], [0, 0, 4, 2]], {0: 3, 1: 2, 3: 0}, [[0, 7, 0, 0], [0, 5, 0, 2], [5, 1, 3, 0], [0, 0, 4, 3]]),
        ([[0, 5, 4, 1], [1, 2, 0, 3], [0, 2, 5, 2], [0, 0, 0, 0]], {0: 0, 1: 2, 3: 1}, [[0, 4, 3, 0], [2, 2, 0, 3], [0, 1, 4, 1], [1, 0, 0, 0]]),
        ([[0, 5, 4, 1], [1, 2, 0, 3], [3, 5, 0, 5], [0, 0, 0, 0]], {0: 0, 1: 2, 3: 1}, [[0, 5, 5, 1], [0, 1, 0, 2], [2, 4, 0, 4], [0, 0, 1, 0]]),
        ([[0, 5, 5, 1], [0, 1, 0, 2], [2, 4, 0, 4], [0, 0, 1, 0]], {0: 0, 1: 2, 3: 1}, [[0, 4, 5, 0], [0, 0, 0, 1], [2, 3, 0, 3], [1, 0, 2, 0]]),
        ([[9, 0, 9, 3], [7, 0, 1, 4], [0, 2, 2, 0], [5, 2, 0, 0]], {0: 1, 2: 0, 3: 2}, [[8, 0, 8, 2], [6, 0, 0, 3], [0, 3, 2, 0], [5, 3, 0, 0]])
    ])
    def test_should_perform_crossing_algorithm_on_cost_matrix(
        self, start_costs, partial_assignment, exp_costs
    ):
        start_costs = np.array(start_costs)
        exp_costs = np.array(exp_costs)
        problem = AssignmentProblem("test_model", start_costs, True)
        norm_problem = NormalizedAssignmentProblem(np.copy(start_costs), problem)

        solver = Solver.__new__(Solver)
        solver.problem = norm_problem

        solver.add_zero_by_crossing_out(solver.problem.costs, partial_assignment)
                
        assert np.array_equal(
            solver.problem.costs, exp_costs
        ), "crossing algorithm is not performed properly:" +\
            f"\n- got: {indented_string(str(solver.problem.costs))}" +\
            f"\n- expected: {indented_string(str(exp_costs))}" +\
            f"\n- for cost matrix: {indented_string(str(start_costs))}" +\
            f"\n- and partial assignment: {partial_assignment}"

    @pytest.mark.parametrize("costs, is_min, norm_costs, assignment, exp_objective", [
        ([[4, 9, 8], [6, 7, 5], [4, 6, 1]], True, [[4, 9, 8], [6, 7, 5], [4, 6, 1]], {0: 0, 2: 2, 1: 1}, 12),
        ([[2, 11, 2, 6], [3, 10, 9, 4], [8, 6, 6, 6], [10, 13, 15, 13]], True, [[2, 11, 2, 6], [3, 10, 9, 4], [8, 6, 6, 6], [10, 13, 15, 13]], {0: 2, 3: 0, 1: 3, 2: 1}, 22),
        ([[2, 11, 2, 1], [3, 10, 3, 4], [8, 6, 6, 2], [11, 13, 15, 13]], True, [[2, 11, 2, 1], [3, 10, 3, 4], [8, 6, 6, 2], [11, 13, 15, 13]], {2: 3, 0: 2, 1: 0, 3: 1}, 20),
        ([[4, 9, 8], [6, 7, 5], [4, 6, 9]], True, [[4, 9, 8], [6, 7, 5], [4, 6, 9]], {0: 0, 2: 1, 1: 2}, 15),
        ([[4, 3, 8], [6, 7, 5], [4, 6, 9], [5, 7, 4]], True, [[4, 3, 8, 0], [6, 7, 5, 0], [4, 6, 9, 0], [5, 7, 4, 0]], {1: 3, 2: 0, 0: 1, 3: 2}, 11),
        ([[4, 9, 8], [6, 7, 5], [4, 6, 9], [5, 7, 4]], True, [[4, 9, 8, 0], [6, 7, 5, 0], [4, 6, 9, 0], [5, 7, 4, 0]], {1: 3, 0: 0, 2: 1, 3: 2}, 14),
        ([[4, 9, 8, 5], [6, 7, 5, 8], [4, 6, 9, 6]], True, [[4, 9, 8, 5], [6, 7, 5, 8], [4, 6, 9, 6], [0, 0, 0, 0]], {1: 2, 2: 0, 0: 3, 3: 1}, 14),
        ([[4, 9, 8, 5], [6, 7, 5, 8], [4, 6, 1, 6]], True, [[4, 9, 8, 5], [6, 7, 5, 8], [4, 6, 1, 6], [0, 0, 0, 0]], {2: 2, 0: 0, 1: 1, 3: 3}, 12),
        ([[2, 11, 2, 6], [3, 10, 9, 4], [8, 6, 6, 6], [10, 13, 15, 13]], False, [[13, 4, 13, 9], [12, 5, 6, 11], [7, 9, 9, 9], [5, 2, 0, 2]], {0: 1, 1: 2, 3: 3, 2: 0}, 41),
        ([[2, 11, 2, 6], [3, 10, 9, 4], [8, 6, 6, 6], [18, 13, 15, 13]], False, [[16, 7, 16, 12], [15, 8, 9, 14], [10, 12, 12, 12], [0, 5, 3, 5]], {0: 1, 1: 2, 3: 0, 2: 3}, 44),
        ([[4, 9, 8], [6, 7, 5], [4, 6, 9], [5, 7, 4]], False, [[5, 0, 1, 0], [3, 2, 4, 0], [5, 3, 0, 0], [4, 2, 5, 0]], {3: 3, 0: 1, 1: 0, 2: 2}, 24),
        ([[4, 7, 8], [6, 7, 5], [4, 6, 9], [5, 7, 4]], False, [[5, 2, 1, 0], [3, 2, 4, 0], [5, 3, 0, 0], [4, 2, 5, 0]], {0: 1, 3: 3, 1: 0, 2: 2}, 22)
    ])
    def test_should_create_proper_assignment_based_on_dict_of_assignments(
        self, costs, is_min, norm_costs, assignment, exp_objective
    ):
        costs = np.array(costs)
        norm_costs = np.array(norm_costs)
        problem = AssignmentProblem("test_model", costs, is_min)
        norm_problem = NormalizedAssignmentProblem(np.copy(norm_costs), problem)

        solver = Solver.__new__(Solver)
        solver.problem = norm_problem

        out_assignment = solver.create_assignment(assignment)

        assert (
            out_assignment.objective == exp_objective
        ), f"hungarian algorithm returns incorrect objective:" +\
            f"\n- got: {out_assignment.objective}" +\
            f"\n- expected: {exp_objective}" +\
            f"\n- for cost matrix: {indented_string(str(problem.costs))}" +\
            f"\n- and assignment: {out_assignment.assigned_tasks}" 

        assert isinstance(out_assignment.assigned_tasks, list), \
            f"the assigned tasks are expected to be returned as list:" +\
            f"\n- got: {out_assignment.assigned_tasks} of type: `{type(out_assignment.assigned_tasks).__name__}`"
            
        meta_inf = f"\n- got assignment: {out_assignment.assigned_tasks}" +\
            f"\n- for cost matrix: {indented_string(str(problem.costs))}"
        assert len(out_assignment.assigned_tasks) >= problem.n_workers(), \
            "the assignment seems to miss a worker:" + meta_inf
        assert len(out_assignment.assigned_tasks) <= problem.n_workers(), \
            "the assignment seems to use non-existing workers:" + meta_inf
        assert max(out_assignment.assigned_tasks) <= problem.n_tasks(), \
            "the assignment seems to assing a non-existing task" + meta_inf
