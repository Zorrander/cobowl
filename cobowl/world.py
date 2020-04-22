from owlready2 import *
from . import state, robot, workspace
import copy
from pathlib import Path

class DigitalWorld():

    def __init__(self, original_world=None, root_task=None, host="https://onto-server-tuni.herokuapp.com"):
        if original_world:
            self.world = World()
            self.onto = self.world.get_ontology( str(Path.home() / 'plan')).load()
        else:
            print("initializing")
            self.world = World()
            self.onto = self.world.get_ontology(host + "/uploads/models/handover.owl").load()
        self.robot = robot.CollaborativeRobot(self.onto)
        self.workspace = workspace.CollaborativeWorkspace(self.onto)
        self.state_interface = state.StateInterface(self.onto)
        self.root_task = list(root_task) if root_task else [self.onto.Be()]

    def create_instance(self, class_name):
        with self.onto:
            return self.world['http://onto-server-tuni.herokuapp.com/Panda#'+ class_name]()

    def dismiss_command(self):
        cmd = self.onto.search_one(type = self.onto.Command)
        if cmd:
            destroy_entity(cmd)

    def clone(self):
        self.onto.save(file = str(Path.home() / 'plan'), format = "rdfxml")
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

    def is_workspace_empty(self):
        return self.workspace.is_empty()

    def send_command(self, command, target=None):
        with self.onto:
            cmd = self.onto.Command()
            cmd.has_action = command
            print("register  {}".format(cmd.__dict__))
            if target:
                cmd.has_target = target

    def find_type(self, task):
        instance_of = task.is_a[0]
        print(instance_of)
        parent = self.onto.get_parents_of(instance_of)[0].name
        print(parent)
        return (instance_of, parent)

    def anchor(self, result):
        print("Concrete method: {}".format(result))
        with self.onto:
            method = result()
            if result.name == "CommandMethod":
                cmd = self.onto.search_one(type = self.onto.Command)
                if cmd.has_action=="give":
                    print("received_give_command({})".format(cmd.__dict__))
                    task = self.onto.HandoverTask()
                elif cmd.has_action=="pack":
                    print("received_pack_command({})".format(cmd.__dict__))
                    task = self.onto.PackingTask()
                elif cmd.has_action=="release":
                    print("received_grelease_command({})".format(cmd.__dict__))
                    task = self.onto.ReleaseTask()
                elif cmd.has_action=="grasp":
                    print("received_grasp_command({})".format(cmd.__dict__))
                    task = self.onto.GraspTask()
                elif cmd.has_action=="reach":
                    print("received_reach_command({})".format(cmd.__dict__))
                    task = self.onto.ReachTask()
                elif cmd.has_action=="pick":
                    print("received_pick_command({})".format(cmd.__dict__))
                    task = self.onto.PickTask()
                else:
                    raise ValueError(cmd.has_action)
                objects = self.onto.search(type = self.onto.Object)
                print("Known objects are {}".format(objects))
                if cmd.has_target:
                    print("anchoring {}".format(cmd.has_target))
                    anchored = []
                    for object in objects:
                        if cmd.has_target in object.is_called:
                            anchored.append(object)
                    if anchored:
                        method.actsOn.append(anchored[0])
                        task.actsOn.append(anchored[0])
                    else:
                        #raise AnchoringError(cmd.has_target)
                        return False
                if not self.are_preconditions_met(task):
                    print("CANNOT SATISFY COMMAND")
                    task = self.onto.IdleTask()
                method.hasSubtask.append(task)
            else:
                print(result.hasSubtask)
                method.hasSubtask = [task() for task in result.hasSubtask]
            return method

    def find_satisfied_method(self, current_task):
        satisfied_methods = set()
        for method in current_task.hasMethod:
            print("hasMethod {}".format(method))
            if self.are_preconditions_met(method):
                print("preconditions are met")
                satisfied_methods.add(method)
        if satisfied_methods:
            return self.has_highest_priority(satisfied_methods)

    def has_highest_priority(self, methods):
        print("possible methods: {}".format(methods))
        max_prio = 100
        result = "cogrob:temp"
        for method in methods:
            priority = method.hasPriority
            if priority < max_prio:
                result = method
                max_prio = priority
        return self.anchor(result)

    def are_preconditions_met(self, primitive):
        print("are_preconditions_met {}".format(primitive))
        with self.onto:
            result = True
            if len(primitive.INDIRECT_hasCondition) > 0:
                for conditions in primitive.INDIRECT_hasCondition:
                    if not self.state_interface.evaluate(conditions.name):
                        result = False
                        break
            return result

    def are_effects_satisfied(self, task):
        with self.onto:
            result = True
            for effects in task.INDIRECT_hasEffect:
                if not self.state_interface.evaluate(effects.name):
                    result = False
                    break
            return result

    def resolve_conflicts(self, diff_vector):
        with self.onto:
            if diff_vector[0] > 0:
                task0 = self.world['http://onto-server-tuni.herokuapp.com/Panda#PickTask']
                task1 = self.world['http://onto-server-tuni.herokuapp.com/Panda#PlaceTask']
                tasks = [task0, task1]
                for task in tasks:
                    task.actsOn = diff_vector[1]
                return tasks

    def find_subtasks(self, method):
        print("find_subtasks({})".format(method))
        return method.hasSubtask

    def apply_effects(self, primitive):
        try:
            with self.onto:
                self.robot.perform(primitive)
                #op = getattr(operator, primitive.INDIRECT_useOperator[0].name)
                #op().run(self.world, primitive, self.robot)
        except Exception as e:
            print(e)
