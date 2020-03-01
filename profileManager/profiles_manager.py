from DAOAmbiosensing import schedule
from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing
from DAOAmbiosensing.profile import Profile
from DAOAmbiosensing.schedule import Schedule
from DAOAmbiosensing.device_configuration import Device_configuration
from DAOAmbiosensing.env_variable_configuration import Env_variable_configuration
from DAOAmbiosensing.environmental_variable import Environmental_variable
from DAOAmbiosensing.activation_strategy import Activation_strategy, Strategy_occupation, Strategy_temporal

class Profiles_Manager:
    buildings_list=[]
    space_actual=None
    dao=None
    profile_actual=None

    def __init__(self,connection):
        self.dao = DAO_ambiosensing()
    ## alterar nomes dos metodos para ser a laPhyton
    def getAllSpaces(self):
        list= self.dao.load_spaces() #fazer no DAO

    def get_active_profile(self):
        #to implement
        return None
    ##def remove_profile(self):
    # check if is not ative and remove all associated.
    def getAtualSpace(self):
        return self.space_actual

    def setAtualSpace(self,id_space):
        if self.space_actual == None or self.space_actual.id_space!=id_space:
            self.space_actual=self.dao.load_space(id_space)

    def getProfile(self,id_profile):
        profile = self.dao.load_profile(id_profile)
        return id_profile

    #get list of profiles from atual space
    def getProfiles(self):
        list=self.dao.load_profiles_by_space(self.space_actual)
        return list

    #get the profile activated in atual-space
    def getActiveProfile(self):
        list=self.getProfiles()
        for profile in list:
            if profile.state:
                return profile
        return None

    #activate a profile of a specific space
    def activateProfile(self,profile):
        profile.state=1
        self.dao.update_profile()

    # desactivate a profile of a specific space
    def desactivateProfile(self, profile):
            profile.state = 0
            self.dao.update_profile()

    def setActualProfile(self,id_profile):
        self.profile_actual=self.dao.load_profiles_by_space(self.space_actual.id_space)

    def getActualProfile(self):
        return self.profile_actual

    def activateActualProfile(self):
        self.profile_actual.state=1
        self.dao.update_profile(self.profile_actual)

    def desactivateActualProfile(self):
        self.profile_actual.state = 1
        self.dao.update_profile(self.profile_actual)

    def createNewProfile(self,name):
        #check if name exist, to be implemented
        if self.space_actual != None:
            profile = Profile(profile_name=name,state=0)
            index = self.dao.save_profile(profile,self.space_actual)
            if index != -1 :
                self.profile_actual=profile
                self.space_actual.add_profile(profile)


    def createSchedule(self,start,end):
        schedule= Schedule(start,end)
        index= self.dao.save_schedule(schedule,self.profile_actual)
        if index != -1 :
            return schedule
        return None

    # get all schedule for the specific profile
    def get_schedules(self):
        list=self.dao.load_schedule_by_profile(self.profile_actual)
        return list

    def add_device_configuration(self,state, value, device, schedule):
        device_configuration= Device_configuration(state=state, operation_value=value,id_device=device.id_device)
        index= self.dao.save_device_configuration(device_configuration,schedule)
        if index != -1:
            schedule.add_device_configuration(device_configuration)
            return device_configuration
        return None

    def add_env_variable_configuration(self,min,max,env_variable,schedule):
        env_variable_configuration= Env_variable_configuration(min=min,max=max,id_env_variable=env_variable.id)
        index= self.dao.save_env_variable_configuration(env_variable_configuration,schedule)
        if index != -1 :
            schedule.add_env_variable_configuration(env_variable_configuration)
            return env_variable_configuration
        return None

    # get  configuration variable for a specific schedule end a specific env_variable
    def get_env_variable_configuration(self,env_variable,schedule):
        list_configurations = self.dao.load_env_variable_configuration_by_schedule(schedule)
        for conf in list_configurations :
            if conf.id_env_variable == env_variable.id:
                return conf
        return None

    # get all configuration for a specific schedule
    def get_env_variable_configurations(self,schedule):
        list_configurations = self.dao.load_env_variable_configuration_by_schedule(schedule)
        return list_configurations

    def get_device_configuration(self,device,schedule):
        list_configurations = self.dao.load_device_configuration_by_schedule(schedule)
        for conf in list_configurations :
            if conf.id_device == device.id:
                return conf
        return None

    def create_activation_strategy_occupation(self, name, min, max):
        strategy_occupation= Strategy_occupation(name=name,min=min,max=max)
        index=self.dao.save_activationSt_occupation(self, strategy_occupation, self.profile_actual)
        if index != -1:
            self.profile_actual.set_activationStrategy(strategy_occupation)
            return strategy_occupation
        return None

        def change__activation_strategy_occupation(self, strategy_occupation, name, min, max):
        # change fields
        strategy_occupation.min = min
        strategy_occupation.max = max
        strategy_occupation.name = name
        # update in database
        self.dao.update_activationSt_occupation(strategy_occupation)
        return strategy_occupation

    def change__activation_strategy_temporal(self, strategy_temporal, name, days, seasons):
        #change fields
        strategy_temporal.list_seasons=seasons;
        strategy_temporal.list_weekdays=days;
        strategy_temporal.name = name
        #update in database
        self.dao.update_activationSt_temporal(strategy_temporal)
        return strategy_temporal

    def create_activation_strategy_temporal(self, name, list_weekdays, list_seasons):
        strategy_temporal = Strategy_temporal(name=name, list_weekdays=list_weekdays, list_seasons=list_seasons)
        index = self.dao.save_activationSt_temporal(self, strategy_temporal, self.profile_actual)
        if index != -1:
            self.profile_actual.set_activationStrategy(strategy_temporal)
            return strategy_temporal
        return None

