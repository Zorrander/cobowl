from owlready2 import *
import copy

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

    def match_objects(self, assembly_set, anchored_objects, list_pairs):
        print(anchored_objects)
        if anchored_objects:
            current_obj = anchored_objects.pop(0)
            match = current_obj.match(assembly_set)
            list_pairs.append((current_obj, match))
            self.match_objects(assembly_set, anchored_objects, list_pairs)
        return list_pairs

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
            task.actsOn.extend(anchored_objects)
            method.hasSubtask.append(task)
        elif cmd.has_action=="pack":
            task = self.onto.PackingTask()
            task.actsOn.extend(anchored_objects)
            target_goal = self.onto.search_one(type = self.onto.Container)
            print("found container for packing task")
            print(target_goal)
            task.has_place_goal = target_goal
            method.hasSubtask.append(task)
        elif cmd.has_action=="release":
            task = self.onto.ReleaseTask()
            task.actsOn.extend(anchored_objects)
            method.hasSubtask.append(task)
        elif cmd.has_action=="grasp":
            task = self.onto.GraspTask()
            task.actsOn.extend(anchored_objects)
            method.hasSubtask.append(task)
        elif cmd.has_action=="reach":
            task = self.onto.ReachTask()
            task.actsOn.extend(anchored_objects)
            method.hasSubtask.append(task)
        elif cmd.has_action=="pick":
            task = self.onto.PickTask()
            task.actsOn.extend(anchored_objects)
            method.hasSubtask.append(task)
        elif cmd.has_action=="assemble":
            pairs = self.match_objects([x for x in anchored_objects], anchored_objects, [])
            print("list_pairs")
            print(pairs)
            for pair in pairs:
                for comp in pairs:
                    if pair[0] in comp and pair[1] in comp:
                        pairs.remove(pair)
            print("pruned_pairs")
            print(pairs)
            for pair in pairs:
                task = self.onto.AssemblyTask()
                task.actsOn.append(pair[0])
                task.actsOn.extend(pair[1])
                method.hasSubtask.append(task)
        else:
            raise ValueError(cmd.has_action)
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
