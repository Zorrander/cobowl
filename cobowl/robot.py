from owlready2 import *
from .state import *


class CollaborativeRobot():

    def __init__(self, onto):
        with onto:
            class Robot(Thing):
                def perform(self, primitive):
                    operator = self._get_operator(primitive.is_a[0].name)
                    return operator()

                def _get_operator(self, primitive):
                    if primitive == "IdleTask" and self.isWaitingForSomething:
                        print("Waiting...")
                        return self._use_idle_operator
                    elif primitive == "WaitForTask":
                        print("Waiting...")
                        self.isWaitingForSomething = True
                        return self._use_idle_operator
                    elif primitive == "IdleTask":
                        print("Nothing to do for now...")
                        return self._use_idle_operator
                    elif primitive == "GraspTask":
                        print("Grasping...")
                        self.isHoldingSomething = True
                        return self._use_close_operator
                    elif primitive == "ReachTask":
                        self.isCapableOfReaching = True
                        print("Reaching...")
                        return self._use_move_operator
                    elif primitive == "ReleaseTask":
                        self.isHoldingSomething = False
                        print("Reaching...")
                        return self._use_open_operator
                        if self.isWaitingForSomething:
                            self.isWaitingForSomething = False
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


            class IdleOperator(Thing):
                def run(self):
                    pass

            class MoveOperator(Thing):
                def run(self):
                    pass

            class OpenOperator(Thing):
                def run(self):
                    pass

            class CloseOperator(Thing):
                def run(self):
                    pass

            self.robot = Robot("panda")
            self.state_interface = StateInterface(onto)

    def perform(self, primitive):
        print("performing {}".format(primitive))
        self.robot.perform(primitive)
