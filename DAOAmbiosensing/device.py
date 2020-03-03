class Device:

    def __init__(self, name, type, id_thingsboard, id_device=None):
        self.id_device = id_device
        self.name = name
        self.type = type
        self.id_thingsboard=id_thingsboard

    def to_string(self):
        return "Device -> name:" + self.name + " id_thingsboard:" + str(self.id_thingsboard) + " type:" + str(self.type)

