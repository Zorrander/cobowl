class AnchoringError(Exception):
   def __init__(self, physical_objects):
      self.objects = physical_objects

class DispatchingError(Exception):
   def __init__(self, primitive):
      self.primitive = primitive
