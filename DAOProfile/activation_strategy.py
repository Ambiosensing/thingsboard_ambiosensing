class Activation_strategy:
    def __init__(self, id, name,profile):
        self.id = id
        self.name = name


class Strategy_alarm(Activation_strategy):
    def __init__(self, id, name, profile, name_alarm, state):
        super().__init__(self, id, name, profile)
        self.name_alarm = name_alarm
        self.state = state


class Strategy_environmental(Activation_strategy):
    def __init__(self, id, name, profile, min, max):
          super().__init__(self, id, name, profile)
          self.min = min
          self.max = max

class Strategy_temporal(Activation_strategy):
    def __init__(self, id, name, profile, list_weekdays, list_seasons):
        super().__init__(self, id, name, profile)
        self.list_weekdays = list_weekdays
        self.list_seasons = list_seasons
