from owlready2 import *

class StateInterface():

    def __init__(self, onto):
        self.onto = onto

    def evaluate(self, state, target = None):
        product = self._get_state(state)
        return product(target)

    def _get_state(self, state):
        if state == "ReceivedCommand":
            return self._has_received_command
        elif state == "IsAligned":
            return self._is_aligned
        elif state == "CanBereleased":
            return self._can_be_released
        elif state == "IsNotHoldingSomething":
            return self._is_not_holding_something
        elif state == "IsNotWaitingForSomething":
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
        elif state == "HumanReady":
            return self._is_human_ready
        elif state == "IsStored":
            return self._is_object_stored
        elif state == "IsNotStored":
            return self._is_object_not_stored
        else:
            raise ValueError(type)

    def _is_object_stored(self, target):
        return True if target.is_stored else False

    def _is_object_not_stored(self, target):
        return True if not target.is_stored else False

    def _can_be_released(self, target):
        return True if target.IsReadyToBeTaken or target.is_stored else False

    def _has_received_command(self, target):
        return True if self.onto.search_one(type = self.onto.Command) else False

    def _is_human_ready(self, target):
        print(self.onto.agent.is_a)
        return True if self.onto.agent.isReady else False

    def _is_human_ready(self, target):
        print(self.onto.agent.is_a)
        return True if self.onto.agent.isReady else False

    def _is_aligned(self, target):
        return self.onto.panda.is_aligned

    def _is_waiting_for_something(self, target):
        return True if not self.onto.panda.isWaitingForSomething else False

    def _is_holding_something(self, target):
        return self.onto.panda.isHoldingSomething

    def _is_not_holding_something(self, target):
        return True if not self.onto.panda.isHoldingSomething else False

    def _is_capable_of_reaching(self, target):
        return self.onto.panda.isCapableOfReaching

    def _is_not_capable_of_reaching(self, target):
        return True if not self.onto.panda.isCapableOfReaching else False

    def _is_ready_to_be_taken(self, target):
        pass

    def _is_not_ready_to_be_taken(self, target):
        pass

class Empty():
    def empty(self):
        print("I need to be emptied")

class Full():
    def fill(self):
        print("I need to be filled")
