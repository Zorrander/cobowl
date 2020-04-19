from owlready2 import *
from .object import *

class CollaborativeWorkspace():

    def __init__(self, onto):
        with onto:
            class Workspace(Thing):

                def is_empty(self):
                    return False if len(self.contains) > 0 else True

            self.workspace = Workspace(contains = [])
            self.sem_obj_interface = SemanticObjectInterface(onto)


    def add_object(self, name):
        object = self.sem_obj_interface.create(name)
        self.workspace.contains.append(object)
        return object
