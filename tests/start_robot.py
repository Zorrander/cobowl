import unittest
import os.path
from os.path import expanduser
from cmd import Cmd
from cobowl import robot

home = expanduser("~")

# RESOURCE_PATH  = os.path.join(home, "ros2_ws", "src", "tuni-semweb", "cobot_knowledge", "resource", "database")
RESOURCE_PATH  = os.path.join(home, "tuni-semweb", "cobot_knowledge", "resource", "database")

class RobotPrompt(Cmd):

    robot = robot.VirtualCollaborativeRobot(os.path.join(RESOURCE_PATH, 'handover.owl'), os.path.join(RESOURCE_PATH, 'user_defined'))
    prompt = '(panda) '
    intro = 'Type help or ? to list commands.\n'

    def do_reset(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        op = self.robot.reset_operator()
        op()

    def do_command(self, arg):
        args = self.parse(arg)
        if len(args) == 2:
            self.robot.run(args)

    def do_bye(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        print('Done.')
        return True

    def parse(self, arg):
        'Convert a series of zero or more numbers to an argument tuple'
        return arg.split()

robot = RobotPrompt()
robot.cmdloop()
