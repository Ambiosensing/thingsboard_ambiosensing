from DAOAmbiosensing.schedule import Schedule

class Profile:
    def __init__(self,profile_name, state, space,id_profile=None,activation_strategy=None):
        self.activation_strategy = activation_strategy
        self.id_profile=id_profile
        self.profile_name=profile_name
        self.state = state
        self.space =space
        self.list_schedule=[]

    def add_schedule(self, schedule):
        self.list_schedule.append(schedule)

    def toString(self):
        return "name"  + self.profile_name + " id " + str(self.id_profile) + "space" + self.space.toString()

    def set_activationStrategy(self, act_strategy):
        self.activation_strategy = act_strategy

