class DeviceHistory:

    def __init__(self, data, id_thingsboard, operation_state, avaiability_state):
        self.id_thingsboard=id_thingsboard
        self.data=data
        self.operation_state = operation_state
        self.avaiability_state=avaiability_state

    def to_string(self):
        return "Device -> data:" + str(self.data) + " id_thingsboard:" + str(self.id_thingsboard) + \
               " operation state:" + str(self.operation_state) + " avaiability " + str(self.avaiability_state)

