from owlready2 import *
from .object import *
from .state import *

class CollaborativeWorkspace():
    def __init__(self, onto):
        self.onto = onto
        self.sem_obj_interface = SemanticObjectInterface(onto)

    def add_object(self, name):
        object = self.sem_obj_interface.create(name)
        object.is_stored = True
        self.onto.cobot_workspace.contains.append(object)
        return object
