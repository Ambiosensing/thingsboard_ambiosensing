class Space:

    def __init__(self, id_space, name, area, occupation_type, building):
        self.id_space = id_space
        self.name = name
        self.area = area
        self.occupation_type = occupation_type
        # self.id_thingsboard = id_thingsboard
        self.profiles = []
        self.building = building

    def add_profile(self, profile):
        self.profiles.append(profile)

    def toString(self):
        return "name " + self.name + " id " + self.id_space + \
               "area " + self.area + "occupation type " + self.occupation_type + \
               "profiles " + self.profiles

