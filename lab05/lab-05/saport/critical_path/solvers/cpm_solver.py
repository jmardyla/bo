import networkx as nx
from ..model import Project
from ..project_network import ProjectState, ProjectNetwork
from typing import List, Dict
from ..solution import FullSolution


class Solver:
    '''
    A "critical path method" solver for the given project.

        Attributes:
    ----------
    project_network: ProjectNetwork
        a project network related to the given project

    Methods:
    --------
    __init__(problem: Project):
        create a solver for the given project
    solve -> FullSolution:
        solves the problem and returns the full solution
    forward_propagation() -> Dict[ProjectState,int]:
        calculates the earliest times the given events (project states) can occur
        returns a dictionary mapping network nodes to the timestamps
    backward_propagation(earliest_times: Dict[ProjectState, int]) -> Dict[ProjectState,int]:
        calculates the latest times the given events (project states) can occur
        uses earliest times to start the computation
        returns a dictionary mapping network nodes to the timestamps
    calculate_slacks(earliest_times: Dict[ProjectState, int], latest_times: Dict[ProjectState,int]) -> Dict[str, int]:
        calculates slacks for every task in the project
        uses earliest times and latest time of the events in the computations
        returns a dictionary mapping tasks names to their slacks
    create_critical_paths(slacks: Dict[str,int]) -> List[List[str]]:
        finds all the critical paths in the project based on the tasks' slacks
        returns list containing paths, every path is a list of tasks names put in the order they occur in the critical path 
    '''
    def __init__(self, problem: Project):
        self.project_network = ProjectNetwork(problem)

    def solve(self) -> FullSolution:
        earliest_times = self.forward_propagation()
        latest_times = self.backward_propagation(earliest_times)
        task_slacks = self.calculate_slacks(earliest_times, latest_times)
        critical_paths = self.create_critical_paths(task_slacks)
        # TODO:
        # set duration of the project based on the gathered data
        duration = None

        return FullSolution(duration, critical_paths, task_slacks)

    def forward_propagation(self) -> Dict[ProjectState, int]:
        # TODO:
        # 1. earliest time of the project start node is always 0
        # 2. every other event can occur as soon as all its predecessors 
        #    plus duration of the tasks leading to the state
        #
        # earliest_times[state] = e
        earliest_times = dict()
        i = 0
        for node in self.project_network.nodes():
            if i == 0:
                earliest_times[self.project_network.start_node] = 0
                i += 1
                continue
            list_of_sums = []
            for predecessor in self.project_network.predecessors(node):
                list_of_sums.append(earliest_times[predecessor] + self.project_network.arc_duration(predecessor, node))

            earliest_times[node] = max(list_of_sums)

        return earliest_times

    def backward_propagation(self, earliest_times: Dict[ProjectState, int]) -> Dict[ProjectState, int]:
        # TODO:
        # 1. latest time of the project goal node always 
        #    equals earliest time of the same node
        # 2. every other event occur has to occur before its successors latest time
        forward_dict = earliest_times

        latest_times = dict()


        i = 0
        for node in reversed(self.project_network.nodes()):
            if i == 0:
                latest_times[self.project_network.goal_node] = forward_dict[self.project_network.goal_node]
                i += 1
                continue
            list_of_sums = []
            for successor in self.project_network.successors(node):
                list_of_sums.append(latest_times[successor] - self.project_network.arc_duration(node, successor))

            latest_times[node] = min(list_of_sums)
        return latest_times

    def calculate_slacks(self, 
                         earliest_times: Dict[ProjectState, int], 
                         latest_times: Dict[ProjectState, int]) -> Dict[str, int]:
        # TODO:
        # 1. slack of the task equals "the latest time of its end" 
        #    minus "earliest time of its start" minus its duration
        # tip: remember to ignore dummy tasks 
        #      - task.is_dummy could be helpful
        #      - read docs of class `Task` in saport/critical_path/model.py
        slacks = dict()
        forward_dict = self.forward_propagation()
        backward_dict = self.backward_propagation(self.forward_propagation())
        for edge in self.project_network.edges():
            if edge[2].is_dummy:
                continue
            slack = backward_dict[edge[1]] - forward_dict[edge[0]] - edge[2].duration
            slacks[edge[2].name] = slack

        return slacks

    def create_critical_paths(self, slacks: Dict[str, int]) -> List[List[str]]:
        # TODO:
        # critical path start connects start node to the goal node
        # and uses only critical tasks (critical task has slack equal 0)
        # 1. create copy of the project network
        # 2. remove all the not critical tasks from the copy
        # 3. find all the paths from the start node to the goal node
        # 4. translate paths (list of nodes) to list of tasks connecting the nodes
        #
        # tip 1. use directly the networkx graph object:
        #        - self.project_network.network or rather its copy (use `.copy()` method)
        # tip 2. use method "remove_edge(<start>, <end>)" directly on the graph object 
        # tip 3. nx.all_simple_paths method finds all the paths in the graph
        # tip 4. if "L" is a list "[1,2,3,4]", zip(L, L[1:]) will return [(1,2),(2,3),(3,4)]
        copy_network = self.project_network.network.copy()

        non_critical_tasks = [task_name for task_name, slack in slacks.items() if slack > 0]
        for start, end, task in self.project_network.edges():
            if task.name in non_critical_tasks:
                copy_network.remove_edge(start, end)

        paths = nx.all_simple_paths(copy_network, self.project_network.start_node, self.project_network.goal_node)

        critical_paths = []
        for path in paths:
            tasks = [self.project_network.arc_task(start, end).name for start, end in zip(path, path[1:]) if not self.project_network.arc_task(start, end).is_dummy]
            critical_paths.append(tasks)

        return critical_paths
