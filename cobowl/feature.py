from owlready2 import *
from .attribute import *

class SemanticFeatureInterface(Thing):

    def __init__(self, onto):
        self.onto = onto
        self.attribute_interface = SemanticAttributeInterface(onto)

    def create(self, type, value=None):
        product = self._get_feature(type)
        return product(value)


    def _get_feature(self, type):
        if type == "boundaries":
            return self._add_boundaries
        elif type == "head":
            return self._add_head
        elif type == "hole":
            return self._add_hole
        elif type == "hollow_space":
            return self._add_hollow_space
        elif type == "profile":
            return self._add_profile
        else:
            raise ValueError(type)

    def _add_boundaries(self, value):
        boundaries = self.onto.Boundaries(has_attribute = [])
        boundaries.has_attribute.append(self.attribute_interface.create("shape", value))
        return boundaries

    def _add_head(self, value):
        head = self.onto.Head(has_attribute = [])
        head.has_attribute.append(self.attribute_interface.create("shape", value))
        return head

    def _add_hollow_space(self, value):
        hollow_space = self.onto.HollowSpace(has_attribute = [])
        hollow_space.has_attribute.append(self.attribute_interface.create("shape", value))
        return hollow_space

    def _add_hole(self, value):
        hole = self.onto.Hole(has_attribute = [])
        hole.has_attribute.append(self.attribute_interface.create("shape", value))
        return hole

    def _add_profile(self, value):
        profile = self.onto.Profile(has_attribute = [])
        profile.has_attribute.append(self.attribute_interface.create("shape", value))
        return profile
