from owlready2 import *
from .feature import *

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
                    else:
                        raise ValueError(type)

                def _create_box(self, feature_interface):
                    box = Box(has_feature = [])
                    box.load_features(feature_interface)
                    return box

            class Box(Object):
                def load_features(self, feature_interface):
                    self.has_feature.append(feature_interface.create("hollow_space", "rectangular"))

            class Container(Thing):
                equivalent_to = [Box]
                
            self.object = Object()
            self.feature_interface = SemanticFeatureInterface(onto)

    def create(self, type):
        return self.object.create(type, self.feature_interface)
