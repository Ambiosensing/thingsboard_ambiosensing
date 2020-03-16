import datetime
from DAOAmbiosensing.schedule import Schedule

class ProfileHistory:
    def __init__(self,id_profile,datetime,state):
        self.datetime = datetime
        self.id_profile=id_profile
        self.state = state

    def toString(self):
        return "ProfileHistory - > date:"  + str(self.datetime) + " id:" + str(self.id_profile) + "state" + str(self.state)



