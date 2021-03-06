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

    def add_profiles(self, list):
        self.profiles.extend(list)

    def add_devices(self, list):
        self.devices.extend(list)

    def add_environment_vars(self, list):
        self.environment_vars.extend(list)

    def to_string(self):
        str_res = "Space -> Name: " + self.name + " | Space id TB: " + str(self.id_thingsboard) + "| Area: " + str(self.area) + \
                  " | Occupation type: " + self.occupation_type + " | Devices: ["

        for device in self.devices:
            str_res += " { " + device.to_string() + " } "
        str_res += "]"

        return str_res




