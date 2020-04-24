from owlready2 import *
from .state import *


class CollaborativeRobot():

    def __init__(self, onto):
        self.onto = onto
        self.robot = onto.panda

    def perform(self, primitive):
        operator = self._get_operator(primitive.is_a[0].name, primitive)
        operator()

    def _get_operator(self, primitive_type, primitive):
        if primitive_type == "IdleTask":
            return self._use_idle_operator()
        elif primitive_type == "WaitForTask":
            self.robot.isWaitingForSomething = True
            return self._use_idle_operator()
        elif primitive_type == "GraspTask":
            self.robot.isHoldingSomething = True
            return self._use_close_operator(primitive.actsOn)
        elif primitive_type == "ReachTask":
            self.robot.isCapableOfReaching = True
            return self._use_move_operator(primitive.actsOn)
        elif primitive_type == "ReleaseTask":
            self.robot.isHoldingSomething = False
            return self._use_open_operator()
            if self.robot.isWaitingForSomething:
                self.robot.isWaitingForSomething = False
        elif primitive_type == "TranslationTask":
            return self._use_move_operator(primitive.has_place_goal)
        elif primitive_type == "AligningTask":
            return self._use_move_operator(primitive.has_place_goal)
        else:
            raise ValueError(type)

    def _use_move_operator(self, target):
        def move_to():
            #self.sem_controller.interpret(primitive)
            print("Moving to {}...".format(target))
        return move_to

    def _use_close_operator(self, target):
        def grasp():
            print("Grasping {}...".format(target))
        return grasp

    def _use_open_operator(self):
        def release():
            print("Releasing...")
        return release

    def _use_idle_operator(self):
        def wait():
            print("Waiting...")
        return wait
