from DAOProfile.schedule import Schedule

class Profile:
    def __init__(self,id_profile,profile_name):
        self.activation_strategy = None
        self.id_profile=id_profile
        self.profile_name=profile_name
        self.list_schedule=[]

    def add_schedule(self,schedule):
        self.list_schedule.append(schedule)

    def toString(self):
        return "name"  + self.profile_name + " id " + self.id_profile

    def set_activationStrategy(self,act_strategy):
        self.activation_strategy = act_strategy

