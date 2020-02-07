

class Device_configuration:
    def __init__(self, id, state, operation_value):
        self.id = id
        self.state = state
        self.operation_value = operation_value
        self.list_devices = []                      #list of devices assigned to this device configuration

    def __init__(self, id, state, operation_value, list_devices):
        self.id = id
        self.state = state
        self.operation_value = operation_value
        self.list_devices = list_devices            # list of devices assigned to this device configuration