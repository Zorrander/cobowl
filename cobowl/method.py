from owlready2 import *

class MethodInterface():

    def __init__(self, onto):
        self.onto = onto

    def create(self, type, current_task):
        product = self._get_method_builder(type)
        return product(type, current_task)

    def _get_method_builder(self, type):
        if type.name == "CommandMethod":
            return self._create_cmd_method
        else:
            return self._create_normal_method

    def _create_cmd_method(self, type, current_task):
        method = self.onto.CommandMethod()
        cmd = self.onto.search_one(type = self.onto.Command)
        robot = self.onto.search_one(type = self.onto.Robot)
        if cmd.has_action=="give":
            task = self.onto.HandoverTask()
        elif cmd.has_action=="pack":
            task = self.onto.PackingTask()
        elif cmd.has_action=="release":
            task = self.onto.ReleaseTask()
        elif cmd.has_action=="grasp":
            task = self.onto.GraspTask()
        elif cmd.has_action=="reach":
            task = self.onto.ReachTask()
        elif cmd.has_action=="pick":
            task = self.onto.PickTask()
        else:
            raise ValueError(cmd.has_action)
        objects = self.onto.search(type = self.onto.Object)
        if cmd.has_target:
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
        #if not self.are_preconditions_met(task):
        #    print("CANNOT SATISFY COMMAND")
        #    task = self.onto.IdleTask()
        method.hasSubtask.append(task)
        return method

    def _create_normal_method(self, type, current_task):
        method = self.onto[type.name]()
        method.hasSubtask = [self.onto[task.name]() for task in type.hasSubtask]
        return method
