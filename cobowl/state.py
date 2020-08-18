from owlready2 import *

class StateInterface():

    def __init__(self, onto):
        self.onto = onto
        with onto:
            class State(Thing):
                def evaluate(self, target = None):
                    print("STATE evaluate()", self.subject.__dict__)
                    subject = onto.search_one(iri =self.subject.iri)
                    print("Evaluating {}({})".format(self, target))
                    print(subject.INDIRECT_get_properties())
                    print(self.INDIRECT_get_properties())
                    for effect_prop in self.INDIRECT_get_properties():
                        if effect_prop in subject.INDIRECT_get_properties():
                            print(getattr(self, 'INDIRECT_'+effect_prop.name))
                            print(getattr(subject, 'INDIRECT_'+effect_prop.name))
                            print("{} is {}".format(self, getattr(self, 'INDIRECT_'+effect_prop.name) == getattr(subject, 'INDIRECT_'+effect_prop.name)))
                            return getattr(self, 'INDIRECT_'+effect_prop.name) == getattr(subject, 'INDIRECT_'+effect_prop.name)
                        else:
                            print("DENIED")

                def apply(self, target = None):
                    print("SETTING NEW VALUE FOR")
                    for effect_prop in self.INDIRECT_get_properties():
                        if not effect_prop.name == 'subject':
                            #if effect_prop in self.subject.INDIRECT_get_properties():
                            print("SETTING NEW VALUE FOR")
                            new_value = getattr(self, 'INDIRECT_'+effect_prop.name)
                            print("{}.{} -> {}".format(self.subject, effect_prop.name, new_value))
                            setattr(self.subject, effect_prop.name, new_value)

    def evaluate(self, state, target):

        #if isinstance(target, list) and len(target) == 1:
        #    target = target[0]
        product = self._get_state(state)
        return product(target)

    def _get_state(self, state):
        if state == "ReceivedCommand":
            return self._has_received_command
        elif state == "IsAligned":
            return self._is_aligned
        elif state == "CanBeReleased":
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
        result = False
        if 'isReadyToBeTaken' in target.__dict__ and target.isReadyToBeTaken:
            result = True
        elif 'is_stored' in target.__dict__ and target.is_stored:
            result = True
        return result

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
        print("Is {} holding SOMETHING ()".format(target))
        if target and target.is_a[0].name == "HumanAgent":
            result = self.onto.agent.isHoldingSomething
        else:
            result = self.onto.panda.isHoldingSomething
        print(result)
        return result

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
