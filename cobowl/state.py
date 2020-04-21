from owlready2 import *

class AnchoringError(Exception):
   def __init__(self, object):
      self.object = object

class SymbolGroundingError(Exception):
    def __init__(self, action_symbol):
        self.action_symbol = action_symbol

class StateInterface():

    def __init__(self, onto):
        with onto:
            class State(Thing):
                def evaluate(self, state):
                    product = self._get_state(state)
                    return product()

                def _get_state(self, state):
                    if state == "ReceivedCommand":
                        return self._has_received_command
                    elif state == "IsNotHoldingSomething":
                        return self._is_not_holding_something
                    elif state == "IsWaitingForSomething":
                        return self._is_waiting_for_something
                    elif state == "IsHoldingSomething":
                        return self._is_holding_something
                    elif state == "IsCapableOfReaching":
                        return self._is_capable_of_reaching
                    elif state == "IsNotCapableOfReaching":
                        return self._is_not_capable_of_reaching
                    elif state == "IsReadyToBeTaken":
                        return self._is_ready_to_be_taken
                    elif state == "IsNotReadyToBeTaken":
                        return self._is_not_ready_to_be_taken
                    else:
                        raise ValueError(type)

                def _has_received_command(self):
                    cond = ReceivedCommand()
                    return cond.evaluate()

                def _is_not_holding_something(self):
                    cond = IsNotHoldingSomething()
                    return cond.evaluate()

                def _is_waiting_for_something(self):
                    cond = IsWaitingForSomething()
                    return cond.evaluate()

                def _is_holding_something(self):
                    cond = IsHoldingSomething()
                    return cond.evaluate()

                def _is_capable_of_reaching(self):
                    cond = IsCapableOfReaching()
                    return cond.evaluate()

                def _is_not_capable_of_reaching(self):
                    cond = IsNotCapableOfReaching()
                    return cond.evaluate()

                def _is_ready_to_be_taken(self):
                    cond = IsReadyToBeTaken()
                    return cond.evaluate()

                def _is_not_ready_to_be_taken(self):
                    cond = IsNotReadyToBeTaken()
                    return cond.evaluate()

            class Empty(State):
                def empty(self):
                    print("I need to be emptied")

            class Full(State):
                def fill(self):
                    print("I need to be filled")

            class ReceivedCommand(State):
                def evaluate(self):
                    if onto.search_one(type = onto.Command):
                        return True
                    else:
                        #raise SymbolGroundingError(cmd.has_action)
                        return False

            class EmptyWorkspace(State):
                def evaluate(self, onto, robot, workspace):
                    return workspace.is_empty()

            class IsWaitingForSomething(State):
                def evaluate(self):
                    return True if ('isWaitingForSomething' in onto.panda.__dict__ and onto.panda.isHoldingSomething == True) else False

            class IsHoldingSomething(State):
                def evaluate(self):
                    return True if ('isHoldingSomething' in onto.panda.__dict__ and onto.panda.isHoldingSomething == True) else False

            class IsNotHoldingSomething(State):
                def evaluate(self):
                    return True if (not 'isHoldingSomething' in onto.panda.__dict__ or onto.panda.isHoldingSomething == False) else False

            class IsCapableOfReaching(State):
                def evaluate(self):
                    result = True if ('isCapableOfReaching' in onto.panda.__dict__ and onto.panda.isCapableOfReaching == True) else False
                    return result

            class IsNotCapableOfReaching(State):
                def evaluate(self):
                    return True if (not 'isCapableOfReaching' in onto.panda.__dict__ or onto.panda.isCapableOfReaching == False) else False

            class IsReadyToBeTaken(State):
                def evaluate(self):
                    return False

            class IsNotReadyToBeTaken(State):
                def evaluate(self):
                    pass

            self.state_interface = State()

    def evaluate(self, condition):
        print("Evaluating {}".format(condition))
        return self.state_interface.evaluate(condition)
