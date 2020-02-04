from DAOProfile.DAO_profiles import DAO_profiles
from DAOProfile.profile import Profile

class Profiles_Manager:
    def __init__(self,connection):
        dao=DAO_profiles(connection)
        profiles_list=dao.load_profiles() #change to hashMap
        activate_profile=None  #profile activated

     def activateProfile(self,id_profile):
         activate_profile=id_profile #change to hashmap