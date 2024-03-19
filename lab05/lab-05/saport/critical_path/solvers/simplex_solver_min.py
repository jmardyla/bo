from ..model import Project
from ..project_network import ProjectNetwork
from ...simplex.model import Model
from ...simplex.expressions.expression import Expression
from ..solution import BasicSolution


class Solver:
    '''
    Simplex based solver looking for the critical path in the project.
    Uses linear model minimizing total duration of the project.

    Attributes:
    ----------
    project_network: ProjectNetwork
        a project network related to the given project
    model: simplex.model.Model
        a linear model looking for the quickest way to finish the project
    Methods:
    --------
    __init__(problem: Project)
        create a solver for the given project
    create_model() -> simplex.model.Model
        builds a linear model of the problem
    solve() -> BasicSolution
        finds the duration of the critical (longest) path in the project network
    '''
    def __init__(self, problem: Project):
        self.project_network = ProjectNetwork(problem)
        self.model = self.create_model()

    def create_model(self) -> Model:
        # TODO:
        # 0) we need as many variables as there are nodes in the project network
        # 1) for each arc in the network, difference between times at its ends has to be
        #    greater or equal duration of the task
        # 2) we have to minimize difference beetwen time of the goal node and the start node
        #
        # tip 1. `self.project_network` is the project network you should use
        #        - read documentation of ProjectNetwork class in 
        #          `saport/critical_path/project_network.py` for guidance
        node_to_var_dict = dict()
        model = Model("critical path (min)")
        list_of_nodes = self.project_network.nodes()
        i = 0
        for node in list_of_nodes:
            var = model.create_variable(f"t{i}")
            node_to_var_dict[node] = var
            i += 1
        
        for edge in self.project_network.edges():
            model.add_constraint(node_to_var_dict[edge[1]] - node_to_var_dict[edge[0]] >= edge[2].duration)

        model.minimize(node_to_var_dict[self.project_network.goal_node] - node_to_var_dict[self.project_network.start_node])
        return model

    def solve(self) -> BasicSolution:
        solution = self.model.solve()
        return BasicSolution(int(solution.objective_value()))
