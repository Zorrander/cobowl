from owlready2 import *
from .object import *
from .state import *

class CollaborativeWorkspace():
    def __init__(self, onto):
        self.onto = onto
        self.workspace = onto.cobot_workspace
        self.sem_obj_interface = SemanticObjectInterface(onto)

    def add_object(self, name):
        object = self.sem_obj_interface.create(name)
        self.workspace.contains.append(object)
        return object
