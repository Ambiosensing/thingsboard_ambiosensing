class Env_variable_configuration:
    def __init__(self, id, min, max):
        self.id = id
        self.min = min
        self.max = max
        self.list_environmental_variables = []                              #list of environmental variables assigned to this env variable configuration

    def __init__(self, id, min, max, list_environmental_variables):
        self.id = id
        self.min = min
        self.max = max
        self.list_environmental_variables = list_environmental_variables    #list of environmental variables assigned to this env variable configuration