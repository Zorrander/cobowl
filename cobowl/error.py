class AnchoringError(Exception):
   def __init__(self, physical_objects):
      self.objects = physical_objects

class GroundingError(Exception):
   def __init__(self, command):
      self.message = "Could not understand {}".format(command)

class DispatchingError(Exception):
   def __init__(self, primitive):
      self.primitive = primitive
