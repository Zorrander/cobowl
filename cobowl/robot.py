import abc
import os.path
from os.path import expanduser
from .world import *
from .planner import *

home = expanduser("~")

class CollaborativeRobotInterface(metaclass=abc.ABCMeta):

    def __init__(self, knowledge_base_path):
        self.world = DigitalWorld(base=knowledge_base_path)
        self.planner = Planner(self.world)

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'move_operator') and
                callable(subclass.move_operator) and
                hasattr(subclass, 'close_operator') and
                callable(subclass.close_operator) and
                hasattr(subclass, 'open_operator') and
                callable(subclass.open_operator) and
                hasattr(subclass, 'idle_operator') and
                callable(subclass.idle_operator) and
                hasattr(subclass, 'stop_operator') and
                callable(subclass.stop_operator) and
                hasattr(subclass, 'reset_operator') and
                callable(subclass.reset_operator) and
                hasattr(subclass, 'connect') and
                callable(subclass.connect) and
                hasattr(subclass, 'notify') and
                callable(subclass.notify))

    def execute(self, command):
        self.send_command(command)
        plan, goal = self.planner.create_plan()
        for action in self.planner.run(plan, goal):
            print(action.__dict__)
            self.perform(action)

    def run(self, command = None):
        try:
            self.send_command(command)
            plan, goal = self.planner.create_plan()
            while not self.world.compare_goal(goal):
                for action in self.planner.run(plan, goal):
                    self.perform(action)
                plan, _ = self.planner.create_plan()
        except DispatchingError as e:
            print("Dispatching Error: {}. Retrying... ".format(e.primitive))
            #new_plan, goal = self.create_plan()
            #self.run(new_plan, goal)

    def production_mode(self):
        ''' TODO: Enter idling mode automatically '''
        pass

    def perform(self, primitive):
        operator = self._get_operator(primitive)
        operator()
        self.notify(primitive)

    def notify(self, task):
        """Trigger an update in each subscriber. """
        print("Subject: Notifying observers...")
        self.world.update(task)

    def _get_operator(self, primitive):
        operator = primitive.is_a[0].INDIRECT_useOperator[0].name
        print("TEST OPERATOR {} - {}".format(primitive, operator))
        if operator == "IdleOperator":
            return self.idle_operator()
        elif operator == "ResetOperator":
            return self.reset_operator()
        elif operator == "StopOperator":
            return self.stop_operator()
        elif operator == "MoveOperator":
            return self.move_operator(primitive.has_place_goal)
        elif operator == "CloseOperator":
            return self.close_operator(primitive.actsOn)
        elif operator == "OpenOperator":
            return self.open_operator(primitive.actsOn)
        else:
            raise ValueError(type)

    @abc.abstractmethod
    def send_command(self, command):
        raise NotImplementedError

    @abc.abstractmethod
    def move_operator(self, target):
        """Move arm to a given position"""
        raise NotImplementedError

    @abc.abstractmethod
    def close_operator(self, target):
        """Robot blindly grasps"""
        raise NotImplementedError

    @abc.abstractmethod
    def open_operator(self, target):
        """Open gripper to full width"""
        raise NotImplementedError

    @abc.abstractmethod
    def idle_operator(self):
        """Robot enters waiting state"""
        raise NotImplementedError

    @abc.abstractmethod
    def stop_operator(self):
        """Stop robot motion"""
        raise NotImplementedError

    @abc.abstractmethod
    def reset_operator(self):
        """Send robot back to home pose"""
        raise NotImplementedError


class VirtualCollaborativeRobot(CollaborativeRobotInterface):

    def __init__(self, knowledge_base_path):
        super().__init__(knowledge_base_path)
        self.world.add_object("peg")

    def send_command(self, command):
        action = command[0]
        target = command[1]
        self.world.send_command(action, target)

    def move_operator(self, target):
        def move_to():
            print("Moving to {}...".format(target))
        return move_to

    def close_operator(self, target):
        def grasp():
            print("Grasping {}...".format(target))
        return grasp

    def open_operator(self, target):
        def release():
            print("Releasing...{}...".format(target))
        return release

    def idle_operator(self):
        def wait():
            print("Waiting...")
        return wait

    def stop_operator(self):
        def stop():
            print("Stopping...")
        return stop

    def reset_operator(self):
        def reset():
            print("Reseting...")
        return reset
