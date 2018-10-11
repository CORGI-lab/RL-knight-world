
class World(object):
    def __init__(self):
        self.agents = [Actor("knight"), Actor("King"), Actor("Dragon"), Actor("Wizard")]


class Agent(object):
    def __init__(self, name):
        self.name = name
        self.inventory = []


class Item(object):
    def __init__(self, name):
        self.name = name
        self.owner = None
        self.purpose = None
