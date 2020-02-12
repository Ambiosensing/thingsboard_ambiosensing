class Space:

    def __init__(self, name, area, occupation_type, building, id_space=None, id_thingsboard=None):
        self.id_space = id_space
        self.name = name
        self.area = area
        self.occupation_type = occupation_type
        self.id_thingsboard = id_thingsboard
        self.profiles = []
        self.devices = []
        self.environment_vars = []
        self.building = building

    def add_profile(self, profile):
        self.profiles.append(profile)

    def add_device(self, device):
        self.devices.append(device)

    def add_environment_var(self, environment_var):
        self.environment_vars.append(environment_var)

    def to_string(self):
        return "Space id: " + str(self.id_space) + " Space id TB: " + str(self.id_thingsboard) +\
               " Name: " + self.name + " Area:" + str(self.area) +\
               " Occupation type:" + self.occupation_type + " Building id: " + self.building.id_building


