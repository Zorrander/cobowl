import unittest
from cobowl import world
from semantic_htn import planner
import os.path
from os.path import expanduser

home = expanduser("~")

RESOURCE_PATH  = os.path.join(home, "ros2", "src", "tuni-semweb", "cobot_knowledge", "resource", "database")

class TestPrimitiveTasks(unittest.TestCase):
    def setUp(self):
        self.world = world.DigitalWorld(base=os.path.join(RESOURCE_PATH, 'handover.owl'))
        self.world.add_object("peg")
        self.planner = planner.Planner(self.world)

    def test_reach(self):
        print("===TEST REACH ===        ")
        plan = self.planner.create_plan(command = ("reach", ["peg"]))
        self.assertEqual(plan[0].name, "reachtask1")
        print()

    def test_grasp(self):
        print("===TEST GRASP===        ")
        plan = self.planner.create_plan(command = ("reach", ["peg"]))
        self.planner.run(self.world, plan)
        plan = self.planner.create_plan(command = ("grasp", ["peg"]))
        self.assertEqual(plan[0].name, "grasptask1")
        print()

    def test_lift(self):
        print("===TEST LIFT===        ")
        plan = self.planner.create_plan(command = ("reach", ["peg"]))
        self.planner.run(self.world, plan)
        plan = self.planner.create_plan(command = ("grasp", ["peg"]))
        self.planner.run(self.world, plan)
        plan = self.planner.create_plan(command = ("lift", ["peg"]))
        self.assertEqual(plan[0].name, "liftingtask1")
        print()

    def test_drop(self):
        print("===TEST DROP===        ")
        plan = self.planner.create_plan(command = ("reach", ["peg"]))
        self.planner.run(self.world, plan)
        plan = self.planner.create_plan(command = ("grasp", ["peg"]))
        self.planner.run(self.world, plan)
        plan = self.planner.create_plan(command = ("lift", ["peg"]))
        self.planner.run(self.world, plan)
        plan = self.planner.create_plan(command = ("drop", ["peg"]))
        self.assertEqual(plan[0].name, "dropingtask1")
        print()

    def test_stop(self):
        print("===TEST STOP===        ")
        plan = self.planner.create_plan( command = ("stop", []))
        self.assertEqual(plan[0].name, "stoptask1")
        print()

    def test_reset(self):
        print("===TEST RESET===        ")
        plan = self.planner.create_plan( command = ("reset", []))
        self.assertEqual(plan[0].name, "resettask1")
        print()

if __name__ == '__main__':
    unittest.main()
