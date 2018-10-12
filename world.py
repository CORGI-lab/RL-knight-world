from typing import List, Tuple

Coords = Tuple[int, int]


class World(object):
    def __init__(self, rows: int=10, cols: int=10, actors: List[Actor]=None,
                 items: List[Item]=None, locations: List[Location]=None):
        self.rows = rows
        self.cols = cols
        self.actors = actors or []
        self.items = items or []
        self.locations = locations or []


class Actor(object):
    def __init__(self, name: str, inventory: List[Item]=None, location: Location=None):
        self.name = name
        self.inventory = inventory or []
        self.location = location or None


class Item(object):
    def __init__(self, name: str, owner: Actor=None, purpose: str=None):
        self.name = name
        self.owner = owner
        self.purpose = purpose


class Location(object):
    def __init__(self, name: str, coords: Coords=(0, 0),
                 actors: List[Actor]=None):
        self.name = name
        self.coords = coords
        self.actors = actors or []


def main():
    actors = [Actor("Knight"), Actor("King"), Actor("Dragon"), Actor("Wizard")]
    items = [Item("Sword"), Item("Enchantment")]
    locations = [Location("Swamp", ), Location("Castle"),
                 Location("Cave"), Location("Forge")]
    print(actors, items, locations)