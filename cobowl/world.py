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

    def compare_goal(self, goal_state, target = None):
        ''' TODO: take subject into account '''
        print("[WORLD compare_goal()]...{}".format(goal_state))
        if not goal_state:  # There is no goal, action deemed successful by default
            return True
        else:
            return goal_state.evaluate(target)

    def clone(self):
        self.onto.save(file = str(Path.home() / 'cobot_logs' / 'plan.owl'), format = "rdfxml")
        return DigitalWorld(original_world=True)

    def is_a_functional_property(self, prop):
        for mother_class in prop.is_a:
            if mother_class.name == "FunctionalProperty":
                return True
        return False

    def add(self, triple_list):
        buffer_list = []
        subjects_dict = {}
        for subject, predicate, obj in triple_list:
            print(subjects_dict)
            if not self.onto[subject] and predicate=='type':
                self.onto[obj](subject)
            else:
                if not subject in subjects_dict.keys():
                    subjects_dict[subject] = {predicate: obj}
                else:
                    subjects_dict[subject].update({predicate: obj})
        print("sorted")
        print(subjects_dict)

        for individual in subjects_dict.keys():
            for prop, value in subjects_dict[individual].items():
                print("{} >> {} >> {}".format(individual, prop, value))
                print("{} >> {} >> {}".format(self.onto[individual] ,self.onto[prop], self.onto[value]))
                if self.is_a_functional_property(self.onto[prop]):
                    print("functional")
                    if self.onto[prop] in self.onto.individuals():
                        setattr(self.onto[individual], prop, self.onto[value])
                        print("added", self.onto[individual], prop, value)
                    else:
                        val = self.onto[value]()
                        setattr(self.onto[individual], prop, self.onto[val])
                        print("added and created", self.onto[individual], prop, val)
                else:
                    print("not functional")
                    val = getattr(self.onto[individual], prop) + [self.onto[value]]
                    print(val)
                    setattr(self.onto[individual], prop,  val)
                    print("added", self.onto[individual], prop, val)
        if buffer_list:
            self.add(buffer_list)

    def add_object(self, name):
        with self.onto:
            obj = self.workspace.add_object(name)
            return obj

    def fetch_available_commands(self):
        objects = self.onto.Command.instances()
        return [obj.get_trigger_word() for obj in objects if obj.get_trigger_word()]

    def fetch_unsatisfied_command(self):
        cmd = self.onto.Command.instances()
        return cmd[0].INDIRECT_has_goal if cmd else False  # TODO: could choose command the most important

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

    def anchor(self, target):
        try:
            print("[World] anchoring {}".format(target))
            for obj in self.onto.search(type = self.onto.Object):
                if target in obj.is_called:
                    real_object = obj
                    break
            if target and not real_object:
                raise AnchoringError(target)
            return real_object
        except Exception as e:
            print(e)

        #self.actsOn = real_object
        #print("[Method builder] method.actsOn -> {}".format(real_object))



    def send_command(self, command, target=None):
        new_cmd = ""
        for cmd in self.onto.search(is_a = self.onto.Command):
            if cmd.get_trigger_word() == command:
                new_cmd = cmd()
                new_cmd.has_action = command
                print("[WORLD send_command() - registered:]", new_cmd.__dict__)
                if target:
                    target = target[0] if type(target) is list else target
                    new_cmd.set_target(target)
                    print("[Command builder] created", new_cmd)
                break
        if not new_cmd:
            raise error.GroundingError(command)
        else:
            self.onto.panda.has_received_command = True
            if not new_cmd.INDIRECT_has_goal in self.onto.individuals():
                print("updating goal")
                goal = new_cmd.INDIRECT_has_goal()
                goal.subject = self.anchor(target)
                new_cmd.has_goal = goal
                print("[WORLD send_command()]", new_cmd.__dict__)
            return new_cmd.INDIRECT_has_goal

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
            print(cond.__dict__)
            cond = self.onto.search_one(iri =cond.iri)
            print("Found conditions: {} over {}".format(cond, primitive.actsOn))
            print("Found conditions: {} over {}".format(cond, primitive.actsOn))
            for x in self.onto.individuals():
                print("ind - {}".format(x))
            if not cond in self.onto.individuals():
                print("update while create instance")
                cond = cond()
                for x in cond.INDIRECT_get_properties():
                    print("{} -- {}".format(cond, getattr(cond, x.name)))
                cond.subject = primitive.actsOn
            if not cond.evaluate(primitive.actsOn):
                print("OOPS RETURNING FALSE")
                return False
        print("OOOH YES RETURNING TRUE")
        return True

    def are_effects_satisfied(self, task):
        result = False
        print("[WORLD] Cheking effect of", task)
        if len(task.is_a[0].INDIRECT_hasEffect) > 0:
            for effect in task.is_a[0].INDIRECT_hasEffect:
                print("[WORLD]",  self.onto.search_one(iri =effect.iri))
                if self.onto.search_one(iri =effect.iri).evaluate(task.actsOn):
                    print("Effect {} was satisfied".format(self.onto.search_one(iri =effect.iri).name))
                    result = True
                    break
        return result

    def find_subtasks(self, method):
        return method.hasSubtask

    def update(self, primitive):
        effects = primitive.is_a[0].INDIRECT_hasEffect
        print("update", primitive.__dict__)
        if primitive.actsOn:
            target = self.onto.search_one(iri =primitive.actsOn.iri)
        self.onto.panda.isWaitingForSomething = False
        for effect in effects:
            e = self.onto.search_one(iri = effect.iri)
            print(e)
            if not e in self.onto.individuals():
                print("update while create instance")
                e = e()
                for x in e.INDIRECT_get_properties():
                    print("{} -- {}".format(e, getattr(e, x.name)))
                e.subject = target
                e.apply()
            else:
                print("update", e)
                e.apply(target)
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
