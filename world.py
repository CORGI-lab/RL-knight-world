from typing import List, Tuple

# TODO: Define all of the transitions.
# + Given a state, return all the possible actions
# + Some actions: up, down, left, right. Enter & exit locations
#     + Actor interactions
#     + Item interactions
#     + Reward for bringing princess back to castle
#     + Punishment for dying. (Eg attack dragon without sword)
# Google methods for doing all this


def save(obj):
    return (obj.__class__, obj.__dict__)


def load(cls, attributes):
    obj = cls.__new__(cls)
    obj.__dict__.update(attributes)
    return obj


class World(object):
    def __init__(self, rows=10, cols=10, actors=None,
                 items=None, locations=None):
        self.rows = rows
        self.cols = cols
        self.actors = actors or []
        self.items = items or []
        self.locations = locations or []
    def __repr__(self):
        return f"{self.rows} x {self.cols} world"


class Actor(object):
    def __init__(self, name=None, location=None, inventory=None):
        self.name = name
        self.inventory = inventory or []
        self.location = location or None
    def __repr__(self):
        return f"Actor {self.name}"


class Item(object):
    default_owner = None
    def __init__(self, name=None, purpose=None, owner=None):
        self.name = name
        self.owner = owner or self.default_owner
        self.purpose = purpose
    def __repr__(self):
        return f"Item {self.name}"


class Location(object):
    def __init__(self, name, coords=(0, 0), actors=None):
        self.name = name
        self.coords = coords
        self.actors = actors or []
    def __repr__(self):
        return f"Location {self.name}"


def main():
    world = World()
    Item.default_owner = world
    actors = [Actor("Knight"), Actor("King"), Actor("Dragon"), Actor("Wizard")]
    items = [Item("Sword"), Item("Enchantment")]
    locations = [Location("Swamp", ), Location("Castle"),
                 Location("Cave"), Location("Forge")]
    print(actors, items, locations)

if __name__ == '__main__':
    main()
