import unittest
import os.path
from os.path import expanduser

from cobowl import robot

home = expanduser("~")

RESOURCE_PATH  = os.path.join(home, "ros2", "src", "tuni-semweb", "cobot_knowledge", "resource", "database")
# RESOURCE_PATH  = os.path.join(home, "tuni-semweb", "cobot_knowledge", "resource", "database")

class TestPrimitiveTasks(unittest.TestCase):
    def setUp(self):
        self.robot = robot.VirtualCollaborativeRobot(os.path.join(RESOURCE_PATH, 'handover.owl'))

    def test_pick_with_reach(self):
        print("===TEST PICK ===        ")
        self.robot.execute(command = ("pick", ["peg"]))
        print()

    def test_pick_without_reach(self):
        print("===TEST PICK ===        ")
        print("REACHING...")
        self.robot.execute(command = ("reach", ["peg"]))
        print("PICK...")
        self.robot.execute(command = ("pick", ["peg"]))
        print()

    def test_place_without_drop(self):
        print("===TEST PLACE ===        ")
        print("PICK")
        self.robot.execute(command = ("pick", ["peg"]))
        print("PLACE")
        self.robot.execute(command = ("place", ["peg"]))
        print()

    def test_place_with_drop(self):
        print("===TEST PLACE ===        ")
        print("PICK")
        self.robot.execute(command = ("pick", ["peg"]))
        print("LIFT")
        self.robot.execute(command = ("lift", ["peg"]))
        print("PLACE")
        self.robot.execute(command = ("place", ["peg"]))
        print()


    def test_handover_robot_to_human(self):
        print("===TEST HANDOVER FROM ROBOT TO HUMAN ===        ")
        self.robot.run(3, command = ("give", ["peg"]))

    def test_handover_human_to_robot(self):
        print("===TEST HANDOVER FROM HUMAN TO ROBOT ===        ")
        self.robot.run(3, command = ("take", ["peg"]))

    '''

    def format_data_for_display(people):
        ...  # Implement this!

    def test_format_data_for_display():
        people = [
            {
                "given_name": "Alfonsa",
                "family_name": "Ruiz",
                "title": "Senior Software Engineer",
            },
            {
                "given_name": "Sayid",
                "family_name": "Khan",
                "title": "Project Manager",
            },
        ]

        assert format_data_for_display(people) == [
            "Alfonsa Ruiz: Senior Software Engineer",
            "Sayid Khan: Project Manager",
        ]
    '''

if __name__ == '__main__':
    unittest.main()
