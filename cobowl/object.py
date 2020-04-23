from owlready2 import *
from .feature import *
from .state import *

class SemanticObjectInterface():

    def __init__(self, onto):
        self.onto = onto
        self.feature_interface = SemanticFeatureInterface(onto)

    def create(self, type):
        product = self._get_object(type)
        return product()

    def _get_object(self, type):
        if type == "box":
            return self._create_box
        elif type == "peg":
            return self._create_peg
        else:
            raise ValueError(type)

    def _create_box(self):
        box = self.onto.Box(has_feature = [], is_called = ["box"])
        box.has_feature.append(self.feature_interface.create("hollow_space", "rectangular"))
        box.has_feature.append(self.feature_interface.create("boundaries", "rectangular"))
        return box

    def _create_peg(self):
        peg = self.onto.Peg(has_feature = [], is_called = ["peg"])
        peg.has_feature.append(self.feature_interface.create("head", "rectangular"))
        return peg
