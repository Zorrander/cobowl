from owlready2 import *

class MethodInterface():

    def __init__(self, onto):
        self.onto = onto

    def create(self, type, current_task):
        product = self._get_method_builder(type)
        return product(type, current_task)

    def anchor(self, physical_objects):
        anchored = list()
        for target in physical_objects:
            real_object = self.onto.search_one(type = self.onto.Object, is_called = target)
            if real_object:
                    anchored.append(real_object)
        return anchored

    def match_objects(self, anchored_objects):
        for o in anchored_objects:
            print(o.__dict__)
            o.match()

    def _get_method_builder(self, type):
        if type.name == "CommandMethod":
            return self._create_cmd_method
        else:
            return self._create_normal_method

    def _create_cmd_method(self, type, current_task):
        method = self.onto.CommandMethod()
        cmd = self.onto.search_one(type = self.onto.Command)
        robot = self.onto.search_one(type = self.onto.Robot)
        anchored_objects = self.anchor(cmd.has_target)
        method.actsOn.extend(anchored_objects)
        if cmd.has_action=="give":
            task = self.onto.HandoverTask()
        elif cmd.has_action=="pack":
            task = self.onto.PackingTask()
            target_goal = self.onto.search_one(type = self.onto.Container)
            print("found container for packing task")
            print(target_goal)
            task.has_place_goal = target_goal
        elif cmd.has_action=="release":
            task = self.onto.ReleaseTask()
        elif cmd.has_action=="grasp":
            task = self.onto.GraspTask()
        elif cmd.has_action=="reach":
            task = self.onto.ReachTask()
        elif cmd.has_action=="pick":
            task = self.onto.PickTask()
        elif cmd.has_action=="assemble":
            pairs = self.match_objects(anchored_objects)
            task = self.onto.AssemblyTask()
        else:
            raise ValueError(cmd.has_action)
        task.actsOn.extend(anchored_objects)
        #if not self.are_preconditions_met(task):
        #    print("CANNOT SATISFY COMMAND")
        #    task = self.onto.IdleTask()
        method.hasSubtask.append(task)
        return method.hasSubtask

    def _create_normal_method(self, type, current_task):
        properties = ['actsOn', 'has_place_goal']
        method = self.onto[type.name]()
        for target in current_task.actsOn:
            for task in type.hasSubtask:
                new_instance=self.onto[task.name]()
                new_instance.actsOn.append(target)
                if current_task.has_place_goal:
                    task.has_place_goal = current_task.has_place_goal
                print(new_instance.__dict__)
                method.hasSubtask.append(new_instance)
        return method.hasSubtask
