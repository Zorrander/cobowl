import unittest
from cmd import Cmd
from pathlib import Path

from cobowl import robot

KB_PATH = str(Path.home() / "semantic_kb" / "system" / "handover.owl")
USER_KB = str(Path.home() / "semantic_kb" / "user")

class RobotPrompt(Cmd):

    robot = robot.VirtualCollaborativeRobot(KB_PATH, USER_KB)
    prompt = '(panda) '
    intro = 'Type help or ? to list commands.\n'

    def do_reset(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        op = self.robot.reset_operator()
        op()

    def do_status(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        print(self.robot.status())

    def do_command(self, arg):
        args = self.parse(arg)
        if len(args) == 2:
            self.robot.send_command(args)

    def do_run(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        self.robot.start()
        args = self.parse(arg)
        if len(args) == 2:
            self.robot.run(command = args)

    def do_start(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        self.robot.start()

    def do_bye(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        self.robot.stop()
        return True

    def parse(self, arg):
        'Convert a series of zero or more numbers to an argument tuple'
        return arg.split()

robot = RobotPrompt()
robot.cmdloop()
