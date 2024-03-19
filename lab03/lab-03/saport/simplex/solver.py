from __future__ import annotations
import sys
from typing import Dict, List

from copy import deepcopy
import saport.simplex.model as ssmod 
import saport.simplex.expressions.objective as sseobj
import saport.simplex.expressions.constraint as ssecon
import saport.simplex.expressions.expression as sseexp
import saport.simplex.solution as sssol
import saport.simplex.tableau as sstab
import numpy as np 

class Solver:
    """
        A class to represent a simplex solver.

        Attributes:
        ______
        _slacks: Dict[Variable, Constraint]:
            contains mapping from slack variables to their corresponding constraints
        _surpluses: Dict[Variable, Constraint]:
            contains mapping from surplus variables to their corresponding constraints
        _artificial: Dict[Variable, Constraint]:
            contains mapping from artificial variables to their corresponding constraints

        Methods
        -------
        solve(model: Model) -> Tableau:
            solves the given model and return the first solution
    """
    _slacks: Dict[sseexp.Variable, ssecon.Constraint]
    _surpluses: Dict[sseexp.Variable, ssecon.Constraint]
    _artificial: Dict[sseexp.Variable, ssecon.Constraint]

    def solve(self, model: ssmod.Model):
        normal_model = self._augment_model(model)
        if len(self._slacks) < len(normal_model.constraints):
            tableau, success = self._presolve(normal_model)
            if not success:
                return sssol.Solution.infeasible(model, tableau, tableau)
        else:
            tableau = self._basic_initial_tableau(normal_model)
        
        initial_tableau = deepcopy(tableau)
        if self._optimize(tableau) == False:
            return sssol.Solution.unbounded(model, initial_tableau, tableau)

        assignment = tableau.extract_assignment()
        return self._create_solution(assignment, model, initial_tableau, tableau)

    def _optimize(self, tableau: sstab.Tableau):
        while not tableau.is_optimal():
            pivot_col = tableau.choose_entering_variable()
            if tableau.is_unbounded(pivot_col):
                return False
            pivot_row = tableau.choose_leaving_variable(pivot_col)

            tableau.pivot(pivot_row, pivot_col)
        return True

    def _presolve(self, model: ssmod.Model):
        """
            _presolve(model: Model) -> Tableau:
                returns an initial tableau for the second phase of simplex
        """
        presolve_model = self._create_presolve_model(model)
        tableau = self._presolve_initial_tableau(presolve_model)
        
        self._optimize(tableau)

        if self._artifical_variables_are_positive(tableau):
            return (tableau, False)

        tableau = self._restore_initial_tableau(tableau, model)
        return (tableau, True)

    def _augment_model(self, original_model: ssmod.Model):
        """
            _augment_model(model: Model) -> Model:
                returns an augmented version of the given model 
        """
        model = deepcopy(original_model)
        model.simplify()
        self._change_objective_to_max(model)
        self._change_constraints_bounds_to_nonnegative(model)
        self._slacks = self._add_slack_variables(model)
        self._surpluses = self._add_surplus_variables(model)   
        return model  

    def _create_presolve_model(self, augmented_model: ssmod.Model):
        presolve_model = deepcopy(augmented_model)
        self._artificial = self._add_artificial_variables(presolve_model)
        return presolve_model    

    def _change_objective_to_max(self, model: ssmod.Model):
        if model.objective.type == sseobj.ObjectiveType.MIN:
            model.objective.invert()
            

    def _change_constraints_bounds_to_nonnegative(self, model: ssmod.Model):
        for constraint in model.constraints:
            if constraint.bound < 0:
                constraint.invert()
    
    def _add_slack_variables(self, model: ssmod.Model) -> List[sseexp.Variable]:
        slacks: Dict[sseexp.Variable, ssecon.Constraint] = dict()

        for constraint in model.constraints:
            if constraint.type == ssecon.ConstraintType.LE:
                slack_var = model.create_variable(f"s{constraint.index}")
                slacks[slack_var] = constraint
                constraint.expression = constraint.expression + slack_var
                constraint.type = ssecon.ConstraintType.EQ

        return slacks

    def _add_surplus_variables(self, model: ssmod.Model) -> List[sseexp.Variable]:
        surpluses: Dict[sseexp.Variable, ssecon.Constraint] = dict()

        for constraint in model.constraints:
            if constraint.type == ssecon.ConstraintType.GE:
                surplus_var = model.create_variable(f"s{constraint.index}")
                surpluses[surplus_var] = constraint
                constraint.expression = constraint.expression - surplus_var
                constraint.type = ssecon.ConstraintType.EQ

        return surpluses 

    def _add_artificial_variables(self, model: ssmod.Model):
        artificial_variables: Dict[sseexp.Variable, ssecon.Constraint] = dict()
        slack_indicies_set = set(slack.index for slack in self._slacks.values())
        artificial_variables_index = 1
        for constraint in model.constraints:
            if constraint.index in slack_indicies_set:
                continue
            new_artificial_variable  = model.create_variable(f"artificial_variable{artificial_variables_index}")
            artificial_variables[new_artificial_variable] = constraint
            artificial_variables_index += 1

        # TODO: add artificial variables to the model.
        #      tip 1. you may base your code on the methods: _add_slack_variables/_add_surplus_variable 
        #      tip 2. artificial variables have to be added only to the constraints without slacks
        #             - self._slacks.values() is a list of constraints where the slacks have been added
        #             - to check if a given constraint is in the list, compare its index with their indices
        #               (constraint class has an `index` attribute, you may use, e.g. c1.index == c2.index)
        return artificial_variables

    def _basic_initial_tableau(self, model: ssmod.Model):
        objective_row = np.array((-1 * model.objective.expression).coefficients(model) + [0.0])
        table = np.array([objective_row] + [c.expression.coefficients(model) + [c.bound] for c in model.constraints])
        return sstab.Tableau(model, table)

    def _presolve_initial_tableau(self, model: ssmod.Model):
        # TODO: create an initial tableau for the artificial variables
        #       - objective row should contain 1.0 for every artificial variable
        #       - then fix the tableau basis (tip. artificial variables should be basic) using simple transformations; 
        #         like in the pivot: subtract rows / multiply by constant
        #       tip 1. you may look at the _basic_initial_tableau on how to create a tableau
        artificial_var_length = len(self._artificial.keys())
        objective_row = np.array( [0.0] * (len(model.objective.expression.coefficients(model))-artificial_var_length)+[1.0]*artificial_var_length + [0.0])
        table = np.array([objective_row] + [c.expression.coefficients(model)+[c.bound] for c in model.constraints])
        for i in self._artificial.keys():
            index = self._artificial[i].index
            table[0] -= table[index+1]

        return sstab.Tableau(model, table)

    def _artifical_variables_are_positive(self, tableau: sstab.Tableau):

        for i in self._artificial.keys():
            if i.index in tableau.extract_basis():
                art_index = self._artificial[i].index+1
            else:
                continue
            # found_ind = tableau.extract_basis().index(art_index)
            if (float(tableau.table[art_index,-1]) > 0):
                return True

        return False

    def _restore_initial_tableau(self, tableau: sstab.Tableau, model: ssmod.Model):
        # TODO: remove artificial variables from the tableau and restore the objective
        #       1. remove corresponding columns from the tableau (`np.delete` is a little helper here)
        #       2. restore the original objective row
        #       3. similarly to the way we have zeroed the artificial variables in `_presolve_initial_tableau`,
        #          now we have to transform the tableau to make the basic variables (basic = being part of the basis) 
        #          in the first phase tableau also basic in the new tableau
        new_table = tableau.table

        for i in self._artificial.keys():
            new_table = np.delete(new_table,-2 , axis=1)
        original_obj_row = (-1 * model.objective.expression).coefficients(model) + [0.0]
        new_table[0] = original_obj_row
        # for i in range(2):
        inds_basis = tableau.extract_basis()
        for i in inds_basis:
            if new_table[0, i] == 0:
                continue
            else:
                index_of_one = np.where(new_table[0:, i] == 1)[0][0]
                new_table[0] = new_table[0]-new_table[index_of_one]*(new_table[0, i])
        # new_tableau = sstab.Tableau(tableau.model, new_table)
        # leaving_var = new_tableau.choose_leaving_variable()
        # new_table = new_tableau.table
        return sstab.Tableau(tableau.model, new_table)

    def _create_solution(self, assignment: List[float], model: ssmod.Model, initial_tableau: sstab.Tableau, tableau: sstab.Tableau):
        return sssol.Solution.with_assignment(model, assignment, initial_tableau, tableau)