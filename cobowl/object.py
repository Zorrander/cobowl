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
        return product(type)

    def _get_object(self, type):
        print("OBJECT")
        print(type)
        if type == "box":
            return self._create_box
        elif type == "peg":
            return self._create_peg
        elif type == "faceplate":
            return self._create_faceplate
        elif type == "separator":
            return self._create_separator
        else:
            return self._create_object

    def _create_box(self, type):
        box = self.onto.Box(has_feature = [], is_called = ["box"])
        box.has_feature.append(self.feature_interface.create("hollow_space", "rectangular"))
        box.has_feature.append(self.feature_interface.create("boundaries", "rectangular"))
        return box

    def _create_peg(self, type):
        peg = self.onto.Peg(has_feature = [], is_called = ["peg"])
        peg.has_feature.append(self.feature_interface.create("head", "rectangular"))
        return peg

    def _create_faceplate(self, type):
        faceplate = self.onto.Faceplate(has_feature = [], is_called = ["faceplate"])
        faceplate.has_feature.append(self.feature_interface.create("hole", "round"))
        faceplate.has_feature.append(self.feature_interface.create("hole", "round"))
        faceplate.has_feature.append(self.feature_interface.create("hole", "round"))
        faceplate.has_feature.append(self.feature_interface.create("hole", "rectangular"))
        faceplate.has_feature.append(self.feature_interface.create("hole", "rectangular"))
        return faceplate

    def _create_separator(self, type):
        separator = self.onto.Separator(has_feature = [], is_called = ["separator"])
        separator.has_feature.append(self.feature_interface.create("hole", "rectangular"))
        separator.has_feature.append(self.feature_interface.create("hole", "rectangular"))
        return separator

    def _create_object(self, type):
        obj = self.onto.Object(has_feature = [], is_called = [type])
        return obj
