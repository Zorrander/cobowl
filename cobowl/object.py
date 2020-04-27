from owlready2 import *
from .feature import *
from .state import *

class SemanticObjectInterface():

    def __init__(self, onto):
        self.onto = onto
        self.feature_interface = SemanticFeatureInterface(onto)
        with onto:
            class Object(Thing):
                    def match(self, candidates):
                        valid = list()
                        for c in candidates:
                            if self.has_compatible_profile(c):
                                valid.append(c)
                                break
                        return valid

                    def has_compatible_profile(self, object):
                        features = [f.is_a[0].name for f in self.has_feature]
                        features2 = [f.is_a[0].name for f in object.has_feature]
                        if "Hole" in features and "Head" in features2:
                            return True
                        elif "Hole" in features2 and "Head" in features:
                            return True
                        else:
                            return False

    def create(self, type):
        product = self._get_object(type)
        return product()

    def _get_object(self, type):
        if type == "box":
            return self._create_box
        elif type == "peg":
            return self._create_peg
        elif type == "faceplate":
            return self._create_faceplate
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

    def _create_faceplate(self):
        peg = self.onto.Faceplate(has_feature = [], is_called = ["faceplate"])
        peg.has_feature.append(self.feature_interface.create("hole", "round"))
        peg.has_feature.append(self.feature_interface.create("hole", "round"))
        peg.has_feature.append(self.feature_interface.create("hole", "round"))
        peg.has_feature.append(self.feature_interface.create("hole", "rectangular"))
        peg.has_feature.append(self.feature_interface.create("hole", "rectangular"))
        return peg
