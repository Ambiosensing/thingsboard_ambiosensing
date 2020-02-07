class Activation_strategy:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Strategy_occupation(Activation_strategy):
    def __init__(self, id, name, min, max):
          super().__init__(self, id, name)
          self.min = min
          self.max = max

class Strategy_temporal(Activation_strategy):
    def __init__(self, id, name, list_weekdays, list_seasons):
        super().__init__(self, id, name)
        self.list_weekdays = list_weekdays
        self.list_seasons = list_seasons
