from .error import *

class Planner():

    def __init__(self, world):
        self.world = world

    def explore_cond_primitive_task(self, current_task, planning_world):
        if planning_world.are_preconditions_met(current_task):
            print("{} - conditions satisfied".format(current_task))
            return True
        else:
            print("{} - conditions unsatisfied".format(current_task))
            return False

    def explore_effects_primitive_task(self, current_task, planning_world):
        return True if planning_world.are_effects_satisfied(current_task) else False

    def explore_compound_task(self, current_task, planning_world):
        return planning_world.find_satisfied_method(current_task)

    def search(self, final_plan, tasks_to_process, planning_world):
        try:
            print("Tasks to process: {}".format(tasks_to_process))
            if tasks_to_process:
                current_task = tasks_to_process.pop(0)
                type = planning_world.find_type(current_task)
                if type == "CompoundTask":
                    new_tasks = self.explore_compound_task(current_task, planning_world)
                    if len(new_tasks) == 1 and new_tasks[0].is_a[0].name == "State":
                        final_plan.insert(0, new_tasks[0])
                    elif new_tasks:
                        print("Found compound task and new tasks are {}".format(new_tasks))
                        tasks_to_process.extend(new_tasks)
                        self.search(final_plan, tasks_to_process, planning_world)
                        #del tasks_to_process[:-len(new_tasks)]
                    else:
                        tasks_to_process.append(current_task)
                        self.search(final_plan, tasks_to_process, planning_world)
                else:  # Primitive task
                    if self.explore_cond_primitive_task(current_task, planning_world):
                        planning_world.update(current_task)
                        self.search(final_plan, tasks_to_process, planning_world)
                        final_plan.insert(0, current_task)
                    else:
                        if not self.explore_effects_primitive_task(current_task, planning_world):
                            tasks_to_process.append(current_task)
                        #tasks_to_process.append(current_task)
                        self.search(final_plan, tasks_to_process, planning_world)
            return final_plan
        except AnchoringError as e:
            print("Propagate anchoring errror - {}".format(e.objects))
            raise

    def create_plan(self, command=None, root_task=None):
        try:
            final_plan = list()
            if command:
                self.world.send_command(command[0], command[1])  # generate a goal
            planning_world = self.world.clone()
            tasks_to_process = planning_world.root_task if not root_task else root_task
            final_plan = self.search(final_plan, tasks_to_process, planning_world)
            goal = planning_world.onto.search_one(type = planning_world.onto.Command)
            goal = goal.has_goal
            print("PLAN: {}".format(final_plan))
            print("GOAL: {}".format(goal))
            return final_plan, goal
        except AnchoringError as e:
            print("Propagate anchoring errror - {}".format(e.objects))
            raise
        except Exception as e:
            print(e)

    def run(self, plan, goal_state = False):
        print("RUN:")
        print("GOAL IS: {}".format(goal_state))
        #while plan and not world.check_state(goal_state):
        while plan:
            primitive = plan.pop(0)
            if self.world.are_preconditions_met(primitive):
                yield primitive
                print("Primitive has effects: {}".format(primitive.hasEffect))
                if self.world.compare_goal(goal_state):
                    print("GOAL WAS REACHED")
                    self.world.dismiss_command()
            else:
                raise DispatchingError(primitive)
