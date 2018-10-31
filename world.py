# TODO: Define all of the transitions.
# + Given a state, return all the possible actions
# + Some actions: up, down, left, right. Enter & exit locations
#     + Actor interactions
#     + Item interactions
#     + Reward for bringing princess back to castle
#     + Punishment for dying. (Eg attack dragon without sword)
# Google methods for doing all this

from copy import deepcopy


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

    def __hash__(self):
        return hash(((self.rows,
                      self.cols,
                      tuple(hash(a) for a in self.actors),
                      tuple(hash(i) for i in self.items),
                      tuple(hash(l) for l in self.locations))))


class Actor(object):
    def __init__(self, name=None, location=None, inventory=None):
        self.name = name
        self.location = location
        self.inventory = inventory or []
        self.alive = True

    def __repr__(self):
        return f"Actor {self.name}"

    def __hash__(self):
        return hash((self.name, self.inventory))


class Item(object):
    default_owner = None

    def __init__(self, name=None, purpose=None, owner=None):
        self.name = name
        self.purpose = purpose
        self.owner = owner or self.default_owner

    def __hash__(self):
        return hash((self.name, self.purpose))

    def __repr__(self):
        return f"Item {self.name}"


class Location(object):
    def __init__(self, name, coords=(0, 0), actors=None):
        self.name = name
        self.coords = coords
        self.actors = actors or []

    def __hash__(self):
        return hash((self.name, self.coords,
                     tuple(hash(a) for a in self.actors)))

    def __repr__(self):
        return f"Location {self.name}"


def A(s):
    agent = None
    if agent.location == "kingdom":
        actions = ["leave"]
        if not king.been_asked:
            actions.append("ask king")
            actions.append("demand king")
        if king.alive:
            actions.append("kill king")
    elif agent.location == "swamp":
        actions = ["leave", "make dinner", "enjoy evening"]
        if "scroll" not in agent.inventory:
            actions.append("pick up scroll")
    elif agent.location == "open world":
        actions = ["left", "right", "up", "down"]
        if agent.coords in [l.coords for l in locations]:
            actions.append("enter")
    elif agent.location == "cave":
        return ["kill dragon", "talk to dragon", ]
    elif agent.location == "armory":
        actions = ["leave"]
        if not wizard.been_requested_already:
            actions.append("request enchantment")
        if wizard.alive:
            actions.append("kill wizard")
    else:
        raise Exception(f"Agent in unknown location: {agent.location}")
    return actions


def R(s, a):
    pass


def T(s, a):
    s = deepcopy(s)
    if a == "kill wizard":
        wizard.alive = False
    if a == "kill king":
        king.alive = False
    if a == "leave":
        s.agent.location = outside_world
    


world = World()
Item.default_owner = world
knight, king, dragon, wizard = \
    Actor("Knight"), Actor("King"), Actor("Dragon"), Actor("Wizard")
actors = [knight, king, dragon, wizard]
items = [Item("Sword", owner=knight), Item("Enchantment", owner=wizard)]
locations = [Location("Swamp", ), Location("Castle"),
             Location("Cave"), Location("Forge")]
world = World(actors=actors, items=items, locations=locations)

world2 = deepcopy(world)
world2.actors[0].name = "Flight"


def p(s):
    print(s, ':', eval(s))


p("world.actors")
p("world2.actors")
p("world.items[0].owner")
p("world2.items[0].owner")
p("items[0]")
p("items[0].owner")
