from DAOProfile.device import Device
from DAOProfile.profile import Profile
from DAOProfile.schedule import Schedule
from DAOProfile.activation_strategy import Activation_strategy,Strategy_alarm,Strategy_environmental,Strategy_temporal


class DAO_profiles:

    def __init__(self, db_connector):
        self.db_connector = db_connector

    def load_devices(self):
 # to replace by a query to database
        device= Device(1,'themometer','avac')
        list.append(self,device);
        return list

    def load_device(self,id):
# to replace by a query to database
        device = Device(id, 'themometer', 'avac')
        return device

    def create_profile(self,profile):
# to replace by a insert to database
        print("creating a new profile.....")
        print(profile.toString())

    def update_profile(self,profile):
        # to replace by a update to database
        print("updating profile.....")
        print(profile.toString())

    def remove_profile(self, id_profile):
        # to replace by update/delete to database
        print("removing profile.....")
        print(id_profile)

    def load_profiles(self):
        # to replace by a query to database
        profile1 = Profile(1,"veraoNormal")
        schedule = Schedule(10, 20, self.load_device(1))
        profile1.add_schedule(schedule)
        st = Strategy_environmental(1,5)
        profile1.set_activationStrategy(st)
        schedule = Schedule(0, 20, self.load_device(2))
        st2 = Strategy_temporal([0,0,0,0,0,0,1,1],[0,1,0,0])
        profile2 = Profile(2, "veraoQuente")
        profile2.add_schedule(schedule)
        profile2.set_activationStrategy(st2)
        list.append(profile1)
        list.append(profile2)
        return list

    def load_profile(self,id):
        # to replace by a query to database
        profile = Profile(id, 'verao')
        schedule = Schedule(10, 20, self.load_device(1))
        profile.add_schedule(schedule)
        st = Strategy_environmental(1, 5)
        profile.set_activationStrategy(st)

        return profile


