class Schedule:
    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end
        self.list_device_configuration = []          #list of device_config assigned to this schedule
        self.list_env_variable_configuration = []    #list of device_config assigned to this schedule

    def __init__(self, id, start, end, list_device_configuration, list_env_variable_configuration):
        self.id = id
        self.start = start
        self.end = end
        self.list_device_configuration = list_device_configuration               #list of device_config assigned to this schedule
        self.list_env_variable_configuration = list_env_variable_configuration   #list of device_config assigned to this schedule

    def add_device_configuration(self,device_configuration):
        self.list_device_configuration.add(device_configuration)

    def add_device_configurations(self, device_configuration_list):
        self.list_device_configuration.extend(device_configuration_list)

    def add_env_variable_configuration(self,env_variable_configuration):
        self.list_env_variable_configuration.add(env_variable_configuration)

    def add_env_variable_configurations(self, env_variable_configuration_list):
        self.list_env_variable_configuration.extend(env_variable_configuration_list)