from ..model import Project
from ..project_network import ProjectNetwork
from ...simplex.model import Model
from ...simplex.expressions.expression import Expression
from ..solution import BasicSolution


class Solver:
    '''
    Simplex based solver looking for the critical path in the project.
    Uses linear model maximizing length of the path in the project network. 

    Attributes:
    ----------
    project_network: ProjectNetwork
        a project network related to the given project
    model: simplex.model.Model
        a linear model looking for the maximal path in the project network
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
        # 0) we need as many variables as there are edges in the project network
        # 1) every variable has to be <= 1
        # 2) sum of the variables starting at the initial state has to be equal 1
        # 3) sum of the variables ending at the goal state has to be equal 1
        # 4) for every other node, total flow going trough it has to be equal 0
        #    i.e. sum of incoming arcs minus sum of the outgoing arcs = 0
        # 5) we have to maximize length of the path
        #    (sum of variables weighted by the durations of the corresponding tasks)
        #
        # tip 1. `self.project_network` is the project network you should use
        #        - read documentation of ProjectNetwork class in 
        #          `saport/critical_path/project_network.py` for guidance

        model = Model("critical path (max)")
        edge_to_var = dict()
        list_of_edges = self.project_network.edges()
        list_of_starting_edges = []
        list_of_ending_edges = []

        for edge in list_of_edges:
            var = model.create_variable(f"x{edge[0].index}{edge[1].index}")
            edge_to_var[edge] = var
            model.add_constraint(var <= 1)
            if edge[0] == self.project_network.start_node:
                list_of_starting_edges.append(var)
            if edge[1] == self.project_network.goal_node:
                list_of_ending_edges.append(var)

        for node in self.project_network.normal_nodes():
            list_of_incoming_edges = []

            for predecessors in self.project_network.predecessors(node):
                edge = (predecessors, node, self.project_network.arc_task(predecessors, node))
                list_of_incoming_edges.append(edge_to_var[edge])

            list_of_outgoing_edges = []
            for successors in self.project_network.successors(node):
                edge = (node, successors, self.project_network.arc_task(node, successors))
                list_of_outgoing_edges.append(edge_to_var[edge])

            model.add_constraint(Expression.from_vectors(list_of_incoming_edges + list_of_outgoing_edges, len(list_of_incoming_edges) * [1] + len(list_of_outgoing_edges) * [-1]) == 0)

        model.add_constraint(Expression.from_vectors(list_of_starting_edges, len(list_of_starting_edges)*[1]) == 1)

        model.add_constraint(Expression.from_vectors(list_of_ending_edges, len(list_of_ending_edges) * [1]) == 1)

        list_of_vars = []
        list_of_arc_tasks = []
        # test czy termin faktycznie jest dłuższy (:o)

        for key in edge_to_var:
            list_of_vars.append(edge_to_var[key])
            list_of_arc_tasks.append(key[2].duration)
        model.maximize(Expression.from_vectors(list_of_vars, list_of_arc_tasks))

        return model

    def solve(self) -> BasicSolution:
        solution = self.model.solve()
        return BasicSolution(int(solution.objective_value()))
