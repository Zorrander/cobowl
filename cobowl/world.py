from owlready2 import *
from pathlib import Path
from . import state, workspace, method, error

class DigitalWorld():
    def __init__(self, original_world=None, root_task=None, base=None):
        self.world = World()
        self.onto = self.world.get_ontology(str(Path.home()/'cobot_logs'/'plan.owl')).load() if original_world else self.world.get_ontology(base).load()
        if original_world:
            cmd = self.onto.search_one(type = self.onto.Robot)
            self.onto.save(file = str(Path.home() / 'cobot_logs' / 'test.owl'), format = "rdfxml")
        #os.remove(str(Path.home() / 'cobot_logs' / 'plan.owl'))
        self.workspace = workspace.CollaborativeWorkspace(self.onto)
        self.method_interface = method.MethodInterface(self.onto)
        self.state_interface = state.StateInterface(self.onto)
        self.root_task = list(root_task) if root_task else [self.onto.be]

    def load_user_knowledge(self, folder_path):
        print("Exploring {}...".format(folder_path))
        directory = Path(folder_path)
        for f in directory.iterdir():
            print("- Found: {}".format(f.name))
            self.world.get_ontology(str(directory / f)).load()

    def dismiss_command(self):
        cmd = self.onto.search_one(type = self.onto.Command)
        if cmd:
            destroy_entity(cmd)

    def compare_goal(self, goal_state):
        ''' TODO: take subject into account '''
        if not 'subject' in goal_state.__dict__:  # There is no goal, action deemed successful by default
            return True
        else:
            print("Checking...{}".format(goal_state.predicate.is_a[0].name))
            return self.state_interface.evaluate(goal_state.predicate.is_a[0].name, goal_state.subject)

    def clone(self):
        self.onto.save(file = str(Path.home() / 'cobot_logs' / 'plan.owl'), format = "rdfxml")
        return DigitalWorld(original_world=True)

    def add_object(self, name):
        with self.onto:
            obj = self.workspace.add_object(name)
            return obj

    def fetch_available_commands(self):
        objects = self.world.search(is_a = self.onto.Command)
        return [obj.get_trigger_word() for obj in objects if obj.get_trigger_word()]

    def sync_reasoner(self):
        try:
            with self.onto:
                sync_reasoner(self.world, debug = True)
        except OwlReadyInconsistentOntologyError:
            print("The ontology is inconsistent")

    def add_object_by_name(self, name):
        with self.onto:
            objects = self.world.search(is_a = self.onto.Object)
            for object in objects:
                if object.is_called == name:
                    self.workspace.contains.append(object())

    def send_command(self, command, target=None):
        new_cmd = ""
        for cmd in self.onto.search(is_a = self.onto.Command):
            if cmd.get_trigger_word() == command:
                new_cmd = cmd()
                new_cmd.has_goal = self.onto.Goal()
                new_cmd.has_action = command
                if target:
                    target = target[0] if type(target) is list else target
                    new_cmd.set_target(target)
                    print("[Command builder] created", new_cmd)
                break
        if not new_cmd:
            raise error.GroundingError(command)
        else:
            self.onto.panda.has_received_command = True

    def find_type(self, task):
        return self.onto.get_parents_of(task.is_a[0])[0].name

    def find_satisfied_method(self, current_task):
        try:
            list_methods = current_task.is_a[0].hasMethod
            print("Found the following methods: {}".format(list_methods))
            method = self.has_highest_priority([method for method in list_methods if self.are_preconditions_met(method)])
            print("Found conditions: {}".format(method.is_a[0].INDIRECT_hasCondition))
            return self.method_interface.create(method, current_task)
        except error.AnchoringError as e:
            print("Propagate anchoring errror - {}".format(e.objects))
            raise
        except Exception as e:
            print(e)

    def has_highest_priority(self, methods):
        max_prio = 100
        result = "cogrob:temp"
        for method in methods:
            priority = method.INDIRECT_hasPriority
            if priority < max_prio:
                result = method
                max_prio = priority
        return result

    def check_state(self, list, target = None):
        result = True
        if len(list) > 0:
            for condition in list:
                if not self.state_interface.evaluate(condition.name, target):
                    print("Condition {} was not satisfied".format(condition.name))
                    result = False
                    break
        return result

    def are_preconditions_met(self, primitive):
        print("are_preconditions_met")
        print("Primitive: {}".format(primitive))
        conditions = primitive.INDIRECT_hasCondition
        #conditions = conditions + primitive.is_a[0].INDIRECT_hasCondition
        for cond in conditions:
            print(cond)
            print(self.onto[cond.name])
            print("Found conditions: {} over {}".format(self.onto.search_one(type = self.onto[cond.name]), primitive.actsOn))
            if not self.onto.search_one(type = self.onto[cond.name]).evaluate(primitive.actsOn):
                return False
        return True

    def are_effects_satisfied(self, task):
        result = False
        if len(task.is_a[0].INDIRECT_hasEffect) > 0:
            for condition in task.is_a[0].INDIRECT_hasEffect:
                if self.state_interface.evaluate(condition.name):
                    print("Effect {} was satisfied".format(condition.name))
                    result = True
                    break
        return result

    def find_subtasks(self, method):
        return method.hasSubtask

    def update(self, primitive):
        print("update", primitive.is_a[0].hasEffect)
        task = primitive.is_a[0].name
        print("update", primitive.__dict__)
        if primitive.actsOn:
            target = primitive.actsOn
        self.onto.panda.isWaitingForSomething = False
        for effect in primitive.is_a[0].hasEffect:
            print(self.onto.search_one(type = self.onto[effect.name]))
            self.onto.search_one(type = self.onto[effect.name]).apply(target)
        '''
        if task == "IdleTask":
            pass
        elif task == "ResetTask":
            pass
        elif task == "StopTask":
            pass
        elif task == "LiftingTask":
            tg = self.onto.search_one(iri = target.iri)
            tg.is_stored = False
        elif task == "DropingTask":
            tg = self.onto.search_one(iri = target.iri)
            tg.is_stored = True
        elif task == "WaitForTask":
            self.onto.panda.isWaitingForSomething = True
        elif task == "GraspTask":
            self.onto.panda.isHoldingSomething = True
        elif task == "ReachTask":
            self.onto.panda.isCapableOfReaching = True
        elif task == "ReleaseTask":
            self.onto.panda.isHoldingSomething = False
        else:
            raise ValueError(type)
        '''

    '''
    def resolve_conflicts(self, diff_vector):
        with self.onto:
            if diff_vector[0] > 0:
                task0 = self.world['http://onto-server-tuni/Panda#PickTask']
                task1 = self.world['http://onto-server-tuni/Panda#PlaceTask']
                tasks = [task0, task1]
                for task in tasks:
                    task.actsOn = diff_vector[1]
                return tasks
    '''
