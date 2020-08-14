from owlready2 import *
from .state import *
import copy
from .error import *
import time

class MethodInterface():

    def __init__(self, onto):
        self.onto = onto
        with onto:
            class Object(Thing): pass
            class Task(Thing): pass
            class Command(Thing):
                @classmethod
                def get_trigger_word(cls):
                    return cls.is_triggered_by

                @classmethod
                def get_triggered_task(cls):
                    return cls.triggers

                def get_target(self):
                    return self.target

                def set_target(self, target):
                    self.target = target

            class PlanRequest(Command): pass

            class Signal(Command): pass

            class is_triggered_by(Command >> str, FunctionalProperty):pass

            class triggers(Command >> Task, FunctionalProperty):
                python_name = "triggers"

            class has_named_target(Command >> str, FunctionalProperty):
                python_name = "target"

            class Method(Thing):
                def anchor(self, target):
                    try:
                        print("[Method builder] anchoring {}".format(target))
                        for obj in onto.search(type = onto.Object):
                            if target in obj.is_called:
                                real_object = obj
                                break
                        if target and not real_object:
                            raise AnchoringError(target)
                        self.actsOn = real_object
                        print("[Method builder] method.actsOn -> {}".format(real_object))
                        return real_object
                    except Exception as e:
                        print(e)

            class Task(Thing):
                def calculate_target_pose(self, target):
                    try:
                        print(target.__dict__)
                        print("[Method builder] creating subtask {}".format(self.INDIRECT_get_properties()))
                        print("[Method builder] creating subtask {}".format(self.INDIRECT_has_path_goal))
                        print("[Method builder] creating subtask {}".format(self.INDIRECT_has_place_goal))
                        self.actsOn = target
                        if not self.INDIRECT_has_place_goal:
                            if not 'is_stored' in target.__dict__ or ('is_stored' in target.__dict__ and target.is_stored):
                                self.has_place_goal.extend([onto.storage])
                            else:
                                self.has_place_goal.extend([onto.handover])
                        else:
                            self.has_place_goal = self.INDIRECT_has_place_goal
                        print("[Method builder] creating subtask >>>>>>>>>>>RESULT {}".format(self.has_place_goal))

                    except Exception as e:
                        print(e)

            class CommandMethod(Method):

                def init_subtasks(self, cmd, anchored_objects):
                    task = cmd.get_triggered_task()
                    task = task()
                    print("[Method builder] creating subtask {}".format(task))
                    task.calculate_target_pose(anchored_objects)
                    time.sleep(3)
                    return [task]

                def create(self):
                    cmd = onto.search_one(type = onto.Command)
                    anchored_object = self.anchor(cmd.get_target())
                    # Create subtasks
                    # and link them to the target_pose and object manipulated
                    return self.init_subtasks(cmd, anchored_object)

    def create(self, type, current_task):
        product = self._get_method_builder(type)
        return product(type, current_task)

    def match_objects(self, assembly_set, anchored_objects, list_pairs):
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
        try:
            method = self.onto.CommandMethod()
            return method.create()
            '''
            cmd = self.onto.search_one(type = self.onto.Command)
            cmd.has_goal = self.onto.Goal()
            anchored_objects = self.anchor(cmd.has_target)
            method.actsOn.extend(anchored_objects)
            '''
            print("Am I here")
            if cmd.has_action=="give":
                task = self.onto.RobotToHumanHandoverTask()
                task.actsOn.extend(anchored_objects)
                method.hasSubtask.append(task)
                cmd.has_goal.subject = self.onto.agent
                cmd.has_goal.predicate = self.onto.IsHoldingSomething()
                if not 'is_stored' in anchored_objects[0].__dict__ or ('is_stored' in anchored_objects[0].__dict__ and anchored_objects[0].is_stored):
                    task.has_place_goal.extend([self.onto.storage])
                else:
                    task.has_place_goal.extend([self.onto.handover])
                print("Command goal becomes: {}".format(cmd.has_goal.__dict__))
            elif cmd.has_action=="take":
                task = self.onto.HumanToRobotHandoverTask()
                task.actsOn.extend(anchored_objects)
                method.hasSubtask.append(task)
                cmd.has_goal.predicate = self.onto.IsStored()
                cmd.has_goal.subject = anchored_objects[0]
                task.has_place_goal.extend([self.onto.handover])
            elif cmd.has_action=="lift":
                task = self.onto.LiftingTask()
                task.actsOn.extend(anchored_objects)
                task.has_place_goal.extend([self.onto.handover])
                cmd.has_goal.predicate = self.onto.IsNotStored()
                cmd.has_goal.subject = anchored_objects[0]
                method.hasSubtask.append(task)
            elif cmd.has_action=="drop":
                task = self.onto.DropingTask()
                task.actsOn.extend(anchored_objects)
                cmd.has_goal.predicate = self.onto.IsStored()
                cmd.has_goal.subject = anchored_objects[0]
                task.has_place_goal.extend([self.onto.storage])
                method.hasSubtask.append(task)
            elif cmd.has_action=="pack":
                task = self.onto.PackingTask()
                task.actsOn.extend(anchored_objects)
                target_goal = self.onto.search_one(type = self.onto.Container)
                print("found container for packing task")
                print(target_goal)
                task.has_place_goal.append(target_goal)
                method.hasSubtask.append(task)
            elif cmd.has_action=="release":
                task = self.onto.ReleaseTask()
                task.actsOn.extend(anchored_objects)
                cmd.has_goal.subject = self.onto.panda
                cmd.has_goal.predicate = self.onto.IsNotHoldingSomething()
                method.hasSubtask.append(task)
            elif cmd.has_action=="grasp":
                task = self.onto.GraspTask()
                cmd.has_goal.predicate = self.onto.IsHoldingSomething()
                cmd.has_goal.subject = self.onto.panda
                task.actsOn.extend(anchored_objects)
                method.hasSubtask.append(task)
            elif cmd.has_action=="reach":
                task = self.onto.ReachTask()
                cmd.has_goal.predicate = self.onto.IsCapableOfReaching()
                cmd.has_goal.subject = self.onto.panda
                task.actsOn.extend(anchored_objects)
                print("Target reach")
                print(anchored_objects[0].__dict__)
                if not 'is_stored' in anchored_objects[0].__dict__ or ('is_stored' in anchored_objects[0].__dict__ and anchored_objects[0].is_stored):
                    task.has_place_goal.extend([self.onto.storage])
                else:
                    task.has_place_goal.extend([self.onto.handover])
                method.hasSubtask.append(task)
                print("Command goal becomes: {}".format(cmd.has_goal.__dict__))
            elif cmd.has_action=="stop":
                task = self.onto.StopTask()
                method.hasSubtask.append(task)
            elif cmd.has_action=="reset":
                task = self.onto.ResetTask()
                method.hasSubtask.append(task)
            elif cmd.has_action=="pick":
                task = self.onto.PickTask()
                cmd.has_goal.predicate = self.onto.IsHoldingSomething()
                cmd.has_goal.subject = self.onto.panda
                task.actsOn.extend(anchored_objects)
                method.hasSubtask.append(task)
                if not 'is_stored' in anchored_objects[0].__dict__ or ('is_stored' in anchored_objects[0].__dict__ and anchored_objects[0].is_stored):
                    task.has_place_goal.extend([self.onto.storage])
                else:
                    task.has_place_goal.extend([self.onto.handover])
                print("Command goal becomes: {}".format(cmd.has_goal.__dict__))
            elif cmd.has_action=="place":
                task = self.onto.PlaceTask()
                task.actsOn.extend(anchored_objects)
                cmd.has_goal.predicate = self.onto.IsStored()
                cmd.has_goal.subject = anchored_objects[0]
                method.hasSubtask.append(task)

                print("Command goal becomes: {}".format(cmd.has_goal.__dict__))
            elif cmd.has_action=="assemble":
                pairs = self.match_objects([x for x in anchored_objects], anchored_objects, [])
                for pair in pairs:
                    for comp in pairs:
                        if pair[0] in comp and pair[1] in comp:
                            pairs.remove(pair)
                for pair in pairs:
                    task = self.onto.AssemblyTask()
                    task.actsOn.append(pair[0])
                    task.has_place_goal.extend(pair[1])
                    method.hasSubtask.append(task)
            else:
                print("Error")
                raise ValueError(cmd.has_action)
        except AnchoringError as e:
            print("Entered anchoring error", e.objects)
            raise
        return method.hasSubtask



    def _create_normal_method(self, type, current_task):
        properties = ['actsOn', 'has_place_goal']
        method = self.onto[type.name]()
        for task in type.hasSubtask:
            new_instance=self.onto[task.name]()
            new_instance.actsOn = current_task.actsOn
            if current_task.has_place_goal:
                print("propagate")
                print(method.hasSubtask)
                if new_instance.is_a[0].name == "LiftingTask":
                    new_instance.has_place_goal = [self.onto.handover]
                else:
                    new_instance.has_place_goal = current_task.has_place_goal
            print("NEW SUBTASK CLASSICAL WAY : {}".format(new_instance.__dict__))
            method.hasSubtask.append(new_instance)
        print("EFFECTS...........")
        print("{}".format(method.INDIRECT_hasEffect))
        if method.INDIRECT_hasEffect:
            method.hasSubtask[0].hasEffect = method.INDIRECT_hasEffect
        return method.hasSubtask
