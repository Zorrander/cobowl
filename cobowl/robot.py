from owlready2 import *
from .state import *


class CollaborativeRobot():

    def __init__(self, onto):
        self.onto = onto

    def perform(self, primitive):
        print("Robot Operator ==> {}".format(primitive.actsOn[0].__dict__))

        operator = self._get_operator(primitive.is_a[0].name, primitive)
        operator()

    def _get_operator(self, primitive_type, primitive):
        self.onto.panda.isWaitingForSomething = False
        if primitive_type == "IdleTask":
            return self._use_idle_operator()
        elif primitive_type == "ResetTask":
            return self._use_reset_operator()
        elif primitive_type == "StopTask":
            return self._use_stop_operator()
        elif primitive_type == "LiftingTask":
            tg = self.onto.search_one(iri = primitive.actsOn[0].iri)
            tg.is_stored = False
            print("Target in real world {}".format(tg.__dict__))
            return self._use_move_operator(primitive.has_place_goal)
        elif primitive_type == "DropingTask":
            # primitive.actsOn[0].is_stored = True
            tg = self.onto.search_one(iri = primitive.actsOn[0].iri)
            tg.is_stored = True
            print("Target in real world {}".format(tg.__dict__))
            return self._use_move_operator(primitive.has_place_goal)
        elif primitive_type == "WaitForTask":
            self.onto.panda.isWaitingForSomething = True
            return self._use_idle_operator()
        elif primitive_type == "GraspTask":
            self.onto.panda.isHoldingSomething = True
            return self._use_close_operator(primitive.actsOn)
        elif primitive_type == "ReachTask":
            self.onto.panda.isCapableOfReaching = True
            return self._use_move_operator(primitive.actsOn)
        elif primitive_type == "InsertingTask":
            self.onto.panda.isAligned = False
            return self._use_move_operator(primitive.actsOn)
        elif primitive_type == "ReleaseTask":
            self.onto.panda.isHoldingSomething = False
            return self._use_open_operator()
        elif primitive_type == "TranslationTask":
            return self._use_move_operator(primitive.has_place_goal)
        elif primitive_type == "AligningTask":
            self.onto.panda.isAligned = True
            return self._use_move_operator(primitive.has_place_goal)
        else:
            raise ValueError(type)

    def _use_move_operator(self, target):
        def move_to():
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

    def _use_stop_operator(self):
        def stop():
            print("Stopping...")
        return stop

    def _use_reset_operator(self):
        def reset():
            print("Reseting...")
        return reset
