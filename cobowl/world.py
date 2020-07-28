from owlready2 import *
from . import state, robot, workspace, method
import copy
from pathlib import Path
import os

class DigitalWorld():
    #def __init__(self, original_world=None, root_task=None, host="https://onto-server-tuni.herokuapp.com"):
    def __init__(self, original_world=None, root_task=None, base=None):
        self.world = World()
        self.onto = self.world.get_ontology(str(Path.home()/'cobot_logs'/'plan.owl')).load() if original_world else self.world.get_ontology(base).load()
        if original_world:
            cmd = self.onto.search_one(type = self.onto.Robot)
            self.onto.save(file = str(Path.home() / 'cobot_logs' / 'test.owl'), format = "rdfxml")
        #os.remove(str(Path.home() / 'cobot_logs' / 'plan.owl'))
        self.robot = robot.CollaborativeRobot(self.onto)
        self.workspace = workspace.CollaborativeWorkspace(self.onto)
        self.method_interface = method.MethodInterface(self.onto)
        self.state_interface = state.StateInterface(self.onto)
        self.root_task = list(root_task) if root_task else [self.onto.be]

    def dismiss_command(self):
        cmd = self.onto.search_one(type = self.onto.Command)
        if cmd:
            destroy_entity(cmd)

    def compare_goal(self, goal_state):
        ''' TODO: take subject into account '''
        print("Checking...{}".format(goal_state.predicate.is_a[0].name))
        return self.state_interface.evaluate(goal_state.predicate.is_a[0].name, goal_state.subject)

    def clone(self):
        self.onto.save(file = str(Path.home() / 'cobot_logs' / 'plan.owl'), format = "rdfxml")
        return DigitalWorld(original_world=True)

    def add_object(self, name):
        with self.onto:
            obj = self.workspace.add_object(name)
            return obj

    def sync_reasoner(self):
        try:
            with self.onto:
                sync_reasoner(self.world, debug = True)
        except OwlReadyInconsistentOntologyError:
            print("The ontology is inconsistent")

    def add_object_by_name(self, name):
        with self.onto:
            objects = self.world.search(is_a = self.onto.Object)
            for object in objects:
                if object.is_called == name:
                    self.workspace.contains.append(object())

    def send_command(self, command, target=None):
        with self.onto:
            cmd = self.onto.Command()
            cmd.has_action = command
            if target:
                list_target = target if type(target) is list else [target]
                cmd.has_target.extend(list_target)

    def find_type(self, task):
        return self.onto.get_parents_of(task.is_a[0])[0].name

    def find_satisfied_method(self, current_task):
        list_methods = current_task.is_a[0].hasMethod
        print("Found the following methods: {}".format(list_methods))
        method = self.has_highest_priority([method for method in list_methods if self.are_preconditions_met(method)])
        print("Found conditions: {}".format(method.is_a[0].INDIRECT_hasCondition))
        return self.method_interface.create(method, current_task)

    def has_highest_priority(self, methods):
        max_prio = 100
        result = "cogrob:temp"
        for method in methods:
            priority = method.INDIRECT_hasPriority
            if priority < max_prio:
                result = method
                max_prio = priority
        return result

    def check_state(self, list, target = None):
        result = True
        if len(list) > 0:
            for condition in list:
                if not self.state_interface.evaluate(condition.name, target):
                    print("Condition {} was not satisfied".format(condition.name))
                    result = False
                    break
        return result

    def are_preconditions_met(self, primitive):
        print("are_preconditions_met")
        print("Primitive: {}".format(primitive))
        print("Found conditions: {} over {}".format(primitive.is_a[0].INDIRECT_hasCondition + primitive.INDIRECT_hasCondition, primitive.actsOn))
        return self.check_state(primitive.is_a[0].INDIRECT_hasCondition+ primitive.INDIRECT_hasCondition, primitive.actsOn)

    def are_effects_satisfied(self, task):
        result = False
        if len(task.is_a[0].INDIRECT_hasEffect) > 0:
            for condition in task.is_a[0].INDIRECT_hasEffect:
                if self.state_interface.evaluate(condition.name):
                    print("Effect {} was satisfied".format(condition.name))
                    result = True
                    break
        return result

    def find_subtasks(self, method):
        return method.hasSubtask

    def apply_effects(self, primitive):
        with self.onto:
            self.robot.perform(primitive)


    '''
    def resolve_conflicts(self, diff_vector):
        with self.onto:
            if diff_vector[0] > 0:
                task0 = self.world['http://onto-server-tuni/Panda#PickTask']
                task1 = self.world['http://onto-server-tuni/Panda#PlaceTask']
                tasks = [task0, task1]
                for task in tasks:
                    task.actsOn = diff_vector[1]
                return tasks
    '''
