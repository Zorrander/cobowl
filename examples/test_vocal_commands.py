from pathlib import Path
from cobowl.robot import VirtualCollaborativeRobot

KB_PATH = str(Path.home() / "semantic_kb" / "system" / "handover.owl")
USER_KB = str(Path.home() / "semantic_kb" / "user")

robot = VirtualCollaborativeRobot(KB_PATH, USER_KB)

while True:
    if not robot.killed:
        robot.start_listening()
    else:
        break
