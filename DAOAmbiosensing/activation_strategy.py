class Activation_strategy:
    def __init__(self, name, id=None):
        self.id = id
        self.name = name


class Strategy_occupation(Activation_strategy):
    def __init__(self, name, min, max, id=None):
          super().__init__(id, name)
          self.min = min
          self.max = max

class Strategy_temporal(Activation_strategy):
    def __init__(self, name, list_weekdays, list_seasons,id=None):
        super().__init__(id, name)
        self.list_weekdays = list_weekdays
        self.list_seasons = list_seasons
