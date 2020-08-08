import abc
import time
import threading
from .world import *
from .planner import *


class CollaborativeRobotInterface(metaclass=abc.ABCMeta):

    def __init__(self, knowledge_base_path, user_folder):
        print("Loading knowledge base")
        self.knowledge_base_path = knowledge_base_path
        self.world = DigitalWorld(base=knowledge_base_path)
        print("Loading user defined concepts")
        self.world.load_user_knowledge(user_folder)
        print("Intializing planner")
        self.planner = Planner(self.world)
        print("Robot up and running")
        commands = self.world.fetch_available_commands()
        self.say_hello(commands)

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'move_operator') and
                callable(subclass.move_operator) and
                hasattr(subclass, 'close_operator') and
                callable(subclass.close_operator) and
                hasattr(subclass, 'open_operator') and
                callable(subclass.open_operator) and
                hasattr(subclass, 'idle_operator') and
                callable(subclass.idle_operator) and
                hasattr(subclass, 'stop_operator') and
                callable(subclass.stop_operator) and
                hasattr(subclass, 'reset_operator') and
                callable(subclass.reset_operator) and
                hasattr(subclass, 'say_hello') and
                callable(subclass.say_hello) and
                hasattr(subclass, 'handle_anchoring_error') and
                callable(subclass.handle_anchoring_error)and
                hasattr(subclass, 'send_command') and
                callable(subclass.send_command)and
                hasattr(subclass, 'pre_notify') and
                callable(subclass.pre_notify)and
                hasattr(subclass, 'post_notify') and
                callable(subclass.post_notify))

    def reload_knowledge(self):
        self.world = DigitalWorld(base=self.knowledge_base_path)
        self.planner = Planner(self.world)
        self.world.add_object("peg")

    def load(self, jsonld_triples):
        self.world.add(jsonld_triples)        

    def status(self):
        robot = self.world.onto.panda
        current_status = [(prop.name, getattr(robot, prop.name)) for prop in robot.INDIRECT_get_properties()]
        return current_status

    def execute(self, command):
        try:
            self.send_command(command)
            plan, goal = self.planner.create_plan()
            for action in self.planner.run(plan, goal):
                print(action.__dict__)
                self.perform(action)
        except Exception as e:
            print(e)

    def run(self, command = None):
        try:
            goal = self.send_command(command)
            plan = self.planner.create_plan()
            while True:
                for action in self.planner.run(plan, goal):
                    self.perform(action)
                if self.world.compare_goal(goal):
                    print("GOAL {} WAS REACHED".format(goal))
                    self.world.dismiss_command()
                    break
                else:
                    plan = self.planner.create_plan()
        except AnchoringError as e:
            print("Propagate anchoring errror - {}".format(e.objects))
            self.handle_anchoring_error(e.objects)
        except DispatchingError as e:
            print("Dispatching Error: {}. Retrying... ".format(e.primitive))
            #new_plan, goal = self.create_plan()
            #self.run(new_plan, goal)

    def production_mode(self):
        ''' TODO: Enter idling mode automatically '''
        try:
            self.killed = False
            print("Robot up and running! You can send commands. \n")
            while True:
                goal = self.world.fetch_unsatisfied_command()
                if goal:
                    plan = self.planner.create_plan()
                    for action in self.planner.run(plan, goal):
                        self.perform(action)
                    if self.world.compare_goal(goal):
                        print("GOAL {} WAS REACHED".format(goal))
                        self.world.dismiss_command()
                else:
                    time.sleep(1)
                if self.killed:
                    break
        except AnchoringError as e:
            print("Propagate anchoring errror - {}".format(e.objects))
            self.handle_anchoring_error(e.objects)
        except DispatchingError as e:
            print("Dispatching Error: {}".format(e.primitive))
            # self.production_mode()

    def start(self):
        run = threading.Thread(target=self.production_mode)
        run.start()

    def stop(self):
        print('Done.')
        self.killed = True

    def perform(self, primitive):
        operator = self._get_operator(primitive)
        self.pre_notify(primitive)
        operator()
        self.world.update(primitive)
        self.post_notify(primitive)

    def _get_operator(self, primitive):
        operator = primitive.is_a[0].INDIRECT_useOperator[0].name
        print("TEST OPERATOR {} - {}".format(primitive, operator))
        if operator == "IdleOperator":
            return self.idle_operator()
        elif operator == "ResetOperator":
            return self.reset_operator()
        elif operator == "StopOperator":
            return self.stop_operator()
        elif operator == "MoveOperator":
            return self.move_operator(primitive.has_place_goal)
        elif operator == "CloseOperator":
            return self.close_operator(primitive.actsOn)
        elif operator == "OpenOperator":
            return self.open_operator(primitive.actsOn)
        else:
            raise ValueError(type)

    @abc.abstractmethod
    def handle_anchoring_error(self, object):
        """Robot enters waiting state"""
        raise NotImplementedError

    @abc.abstractmethod
    def handle_grounding_error(self, object):
        """Robot enters waiting state"""
        raise NotImplementedError

    @abc.abstractmethod
    def say_hello(self, commands):
        """Robot enters waiting state"""
        raise NotImplementedError

    @abc.abstractmethod
    def pre_notify(self, task):
        raise NotImplementedError

    @abc.abstractmethod
    def post_notify(self, task):
        raise NotImplementedError

    @abc.abstractmethod
    def send_command(self, command):
        raise NotImplementedError

    @abc.abstractmethod
    def move_operator(self, target):
        """Move arm to a given position"""
        raise NotImplementedError

    @abc.abstractmethod
    def close_operator(self, target):
        """Robot blindly grasps"""
        raise NotImplementedError

    @abc.abstractmethod
    def open_operator(self, target):
        """Open gripper to full width"""
        raise NotImplementedError

    @abc.abstractmethod
    def idle_operator(self):
        """Robot enters waiting state"""
        raise NotImplementedError

    @abc.abstractmethod
    def stop_operator(self):
        """Stop robot motion"""
        raise NotImplementedError

    @abc.abstractmethod
    def reset_operator(self):
        """Send robot back to home pose"""
        raise NotImplementedError


class VirtualCollaborativeRobot(CollaborativeRobotInterface):

    def __init__(self, knowledge_base_path, user_folder):
        super().__init__(knowledge_base_path, user_folder)
        self.world.add_object("peg")

    def say_hello(self, commands):
        print('\n PANDA PLATFORM INTERFACE')
        print('======================== \n')
        print('To command the robot use one of the following trigger words: \n')
        for cmd in commands:
            print("- {}".format(cmd))

    def pre_notify(self, task):
        print("About to perform {}".format(task))

    def post_notify(self, task):
        print("{} completed".format(task))

    def send_command(self, command):
        try:
            action = command[0]
            target = command[1]
            return self.world.send_command(action, target)
        except error.GroundingError as e:
            self.handle_grounding_error(e.object)

    def move_operator(self, target):
        def move_to():
            print("Moving to {}...".format(target))
        return move_to

    def close_operator(self, target):
        def grasp():
            print("Grasping {}...".format(target))
        return grasp

    def open_operator(self, target):
        def release():
            print("Releasing...{}...".format(target))
        return release

    def idle_operator(self):
        def wait():
            print("Waiting...")
        return wait

    def stop_operator(self):
        def stop():
            print("Stopping...")
        return stop

    def reset_operator(self):
        def reset():
            print("Reseting...")
            self.stop()
            self.reload_knowledge()
        return reset

    def handle_anchoring_error(self, object):
        print("COULD NOT ANCHOR", object)

    def handle_grounding_error(self, object):
        print("COULD NOT GROUND", object)
