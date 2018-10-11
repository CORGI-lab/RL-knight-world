class World(object):
    def __init__(self):
        self.num_rows = 10
        self.num_cols = 10
        self.actors = [Actor("Knight"), Actor("King"),
                       Actor("Dragon"), Actor("Wizard")]
        self.items = [Item("Sword"), Item("Enchantment")]
        self.locations = [Location("Swamp", ), Location("Castle"),
                          Location("Cave"), Location("Forge")]


class Actor(object):
    def __init__(self, name, inventory=None, location=None):
        self.name = name
        self.inventory = inventory or []
        self.location = location


class Item(object):
    def __init__(self, name):
        self.name = name
        self.owner = None
        self.purpose = None


class Location(object):
    def __init__(self, name, coords, actors):
        self.name = name
        self.coords = coords
        self.actors = []  # actors inside this location