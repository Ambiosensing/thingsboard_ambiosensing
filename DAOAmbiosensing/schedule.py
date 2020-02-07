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