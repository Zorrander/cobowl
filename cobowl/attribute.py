from owlready2 import *
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class SemanticAttributeInterface(Thing):

    def __init__(self, onto):
        self.onto = onto

    def create(self, type, value):
        product = self._get_attribute(type)
        return product(value)

    def _get_attribute(self, type):
        if type == "size":
            return self._attach_size
        elif type == "shape":
            return self._attach_shape
        elif type == "color":
            return self._attach_color
        else:
            raise ValueError(type)

    def _attach_size(self, value):
        size = Size()
        return size.create_size(size.compute(value))

    def _attach_shape(self, value):
        if value == "rectangular":
            return self._make_rectangular
        elif value == "round":
            return self._make_round
        else:
            raise ValueError(value)

    def _make_rectangular(self):
        return self.onto.Rectangular()

    def _make_round(self):
        return self.onto.Round()

    def _attach_color(self, value):
        return self.onto.Color()

'''


class Size(Attribute):
    width = np.arange(0, 11, 1)
    #length = np.arange(0, 11, 1)
    #diameter = np.arange(0, 11, 1)
    size = np.arange(0, 26, 1)

    width_s = fuzz.trimf(width, [0, 0, 5])
    width_m = fuzz.trimf(width, [2, 5, 8])
    width_l = fuzz.trimf(width, [5, 10, 10])
    #length_lo = fuzz.trimf(length, [0, 0, 5])
    #length_md = fuzz.trimf(length, [0, 5, 10])
    #length_hi = fuzz.trimf(length, [5, 10, 10])
    #diameter_lo = fuzz.trimf(diameter,  [0, 0, 5])
    #diameter_md = fuzz.trimf(diameter,  [0, 5, 10])
    #diameter_hi = fuzz.trimf(diameter, [5, 10, 10])
    size_s = fuzz.trimf(size, [0, 0, 13])
    size_m = fuzz.trimf(size, [5, 13, 20])
    size_l = fuzz.trimf(size, [13, 25, 25])
    categories = [('Small', size_s), ('Medium', size_m), ('Big', size_l)]

    #serv_level_lo = fuzz.interp_membership(x_serv, serv_lo, 9.8)
    #serv_level_md = fuzz.interp_membership(x_serv, serv_md, 9.8)
    #serv_level_hi = fuzz.interp_membership(x_serv, serv_hi, 9.8)


    def interpret_output(self, value):
        max = 0
        result = ""
        for name, c_fun in self.categories:
            activation = fuzz.interp_membership(self.size, c_fun, value)
            if activation >  max:
                max = activation
                result = name
        return result

    def compute(self, width):
        width_level_s = fuzz.interp_membership(self.width, self.width_s, width)
        width_level_m = fuzz.interp_membership(self.width, self.width_m, width)
        width_level_l = fuzz.interp_membership(self.width, self.width_l, width)

        size_activation_lo = np.fmin(width_level_s, self.size_s)
        size_activation_md = np.fmin(width_level_m, self.size_m)
        size_activation_hi = np.fmin(width_level_l, self.size_l)
        # Aggregate all three output membership functions together
        aggregated = np.fmax(size_activation_lo,
                             np.fmax(size_activation_md, size_activation_hi))

        # Calculate defuzzified result
        size_result = fuzz.defuzz(self.size, aggregated, 'centroid')
        size_activation = fuzz.interp_membership(self.size, aggregated, size_result)
        category = self.interpret_output(size_result)
        return category, aggregated, size_result, size_activation

        self.attribute = Attribute()
'''
