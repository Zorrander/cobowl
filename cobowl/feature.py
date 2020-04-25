from owlready2 import *
from .attribute import *

class SemanticFeatureInterface(Thing):

    def __init__(self, onto):
        with onto:
            class has_feature(ObjectProperty): pass

            class Feature(Thing):

                def create_feature(self, type, attribute_interface, value=None):
                    product = self._get_feature(type)
                    return product(attribute_interface, value)

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

                def _add_boundaries(self, attribute_interface, value):
                    boundaries = Boundaries(has_attribute = [])
                    boundaries.load_attributes(attribute_interface, value)
                    return boundaries

                def _add_head(self, attribute_interface, value):
                    head = Head(has_attribute = [])
                    head.load_attributes(attribute_interface, value)
                    return head

                def _add_hollow_space(self, attribute_interface, value):
                    hollow_space = HollowSpace(has_attribute = [])
                    hollow_space.load_attributes(attribute_interface, value)
                    return hollow_space

                def _add_hole(self, attribute_interface, value):
                    hole = Hole(has_attribute = [])
                    hole.load_attributes(attribute_interface, value)
                    return hole

                def _add_profile(self, attribute_interface, value):
                    profile = Profile(has_attribute = [])
                    profile.load_attributes(attribute_interface, value)
                    return profile

            class HollowSpace(Feature):
                def load_attributes(self, attribute_interface, value):
                    self.has_attribute.append(attribute_interface.create("shape", value))

            class Boundaries(Feature):
                def load_attributes(self, attribute_interface, value):
                    self.has_attribute.append(attribute_interface.create("shape", value))

            class Head(Feature):
                def load_attributes(self, attribute_interface, value):
                    self.has_attribute.append(attribute_interface.create("shape", value))

            class Hole(Feature):
                def load_attributes(self, attribute_interface, value):
                    self.has_attribute.append(attribute_interface.create("shape", value))

            class Profile(Feature):
                def load_attributes(self, attribute_interface, value):
                    self.has_attribute.append(attribute_interface.create("shape", value))

            self.feature = Feature()
            self.attribute_interface = SemanticAttributeInterface(onto)

    def create(self, type, value=None):
        return self.feature.create_feature(type, self.attribute_interface, value)
