from owlready2 import *
from .feature import *
from .state import *

class SemanticObjectInterface():

    def __init__(self, onto):
        with onto:

            class Object(Thing):
                def create(self, type, feature_interface):
                    product = self._get_object(type)
                    return product(feature_interface)

                def _get_object(self, type):
                    if type == "box":
                        return self._create_box
                    elif type == "peg":
                        return self._create_peg
                    else:
                        raise ValueError(type)

                def _create_box(self, feature_interface):
                    box = Box(has_feature = [], is_called = ["box"])
                    box.load_features(feature_interface)
                    return box

                def _create_peg(self, feature_interface):
                    peg = Peg(has_feature = [])
                    peg.load_features(feature_interface)
                    return peg

            class Container(Object):
                def add(self, object):
                    self.contains.append(object)

            class Box(Object):
                def load_features(self, feature_interface):
                    self.has_feature.append(feature_interface.create("hollow_space", "rectangular"))
                    self.has_feature.append(feature_interface.create("boundaries", "rectangular"))

            class Peg(Object):
                def load_features(self, feature_interface):
                    self.has_feature.append(feature_interface.create("head", "rectangular"))

            self.object = Object()
            self.feature_interface = SemanticFeatureInterface(onto)
            self.state_interface = StateInterface(onto)

    def create(self, type):
        return self.object.create(type, self.feature_interface)
