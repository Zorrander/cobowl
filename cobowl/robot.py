from owlready2 import *
from .state import *


class CollaborativeRobot():

    def __init__(self, onto):
        self.onto = onto
        self.robot = onto.panda

    def perform(self, primitive):
        operator = self._get_operator(primitive.is_a[0].name)
        operator(primitive.actsOn)

    def _get_operator(self, primitive):
        if primitive == "IdleTask":
            return self._use_idle_operator
        elif primitive == "WaitForTask":
            self.robot.isWaitingForSomething = True
            return self._use_idle_operator
        elif primitive == "GraspTask":
            self.robot.isHoldingSomething = True
            return self._use_close_operator
        elif primitive == "ReachTask":
            self.robot.isCapableOfReaching = True
            return self._use_move_operator
        elif primitive == "ReleaseTask":
            self.robot.isHoldingSomething = False
            return self._use_open_operator
            if self.robot.isWaitingForSomething:
                self.robot.isWaitingForSomething = False
        elif primitive == "TranslationTask":
            return self._use_move_operator
        else:
            raise ValueError(type)

    def _use_move_operator(self):
        operator = MoveOperator()
        operator.run()

    def _use_close_operator(self):
        operator = CloseOperator()
        operator.run()

    def _use_open_operator(self):
        operator = OpenOperator()
        operator.run()

    def _use_idle_operator(self):
        operator = IdleOperator()
        operator.run()


class IdleOperator():
    def run(self):
        pass

class MoveOperator():
    def run(self):
        pass

class OpenOperator():
    def run(self):
        pass

class CloseOperator():
    def run(self):
        pass
