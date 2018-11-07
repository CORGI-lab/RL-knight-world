# TODO: Define all of the transitions.
# + Given a state, return all the possible actions
# + Some actions: up, down, left, right. Enter & exit locs
#     + Actor interactions
#     + Item interactions
#     + Reward for bringing princess back to castle
#     + Punishment for dying. (Eg attack dragon without sword)
# Google methods for doing all this
# Structure:
# One state is the entire world.
# The world contains actors, items, and locs, which are all objects.
# Only the agent can take actions. Actions are strings.
#  Most actions are deterministic.
from random import random
from collections import defaultdict
from time import sleep


def Q_learning(s0, A, RT, is_terminal, draw, n=100, 𝛼=.2, ε=.05, ɣ=.95):
    Q = defaultdict(int)
    S = set()
    for _ in range(n):
        s = s0
        while True:
            draw(s)
            sleep(.1)
            S.add(s)
            if is_terminal(s):
                break
            a = (random.choice(A)
                 if random.random() < ε
                 else max(A, key=lambda a: Q[s, a]))
            r, s2 = RT(s, a)
            max_s2 = max(Q[s2, a] for a in A)
            Q[s, a] += 𝛼 * (r + ɣ * max_s2 - Q[s, a])
            s = s2
    π = {s: max(A, lambda a: Q[s, a])
         for s in S}
    return π


class World(object):
    def __init__(self, rows=10, cols=10, actors=None,
                 items=None, locs=None):
        self.rows = rows
        self.cols = cols
        self.actors = {actor.name: actor for actor in actors}
        self.items = {item.name: item for item in items}
        self.locs = {loc.name: loc for loc in locs}
        self.loc_coords = {loc.coords for loc in locs}
        self.agent = Agent()

    def __repr__(self):
        return f'{self.rows} x {self.cols} world'

    def __hash__(self):
        return hash(((self.rows,
                      self.cols,
                      tuple(hash(a) for a in self.actors),
                      tuple(hash(i) for i in self.items),
                      tuple(hash(l) for l in self.locs))))


class Actor(object):
    def __init__(self, name=None, loc=None, inventory=None):
        self.name = name
        self.loc = loc
        self.coords = None
        self.inventory = inventory or []
        self.alive = True

    def __repr__(self):
        return f'Actor {self.name}'

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
        return f'Item {self.name}'


class Loc(object):
    def __init__(self, name, coords, actors=None):
        self.name = name
        self.coords = coords
        self.actors = actors or []

    def __hash__(self):
        return hash((self.name, self.coords,
                     tuple(hash(a) for a in self.actors)))

    def __repr__(self):
        return f'loc {self.name}'


class Agent(object):
    def __init__(self):
        pass


def A(s):
    loc = s.agent.loc
    if loc == s.locs['kingdom']:
        acts = ['leave']
        king = s.actors['king']
        if not king.been_asked:
            acts.append('ask king')
            acts.append('demand king')
        if king.alive:
            acts.append('kill king')
    elif loc == s.locs['swamp']:
        acts = ['leave', 'make dinner', 'enjoy evening']
        if 'scroll' not in s.agent.inventory:
            acts.append('pick up scroll')
    elif loc == s.locs['open world']:
        acts = []
        r, c = s.agent.coords
        if r > 0:
            acts.append('up')
        if r < s.rows:
            acts.append('down')
        if c > 0:
            acts.append('left')
        if c < s.cols:
            acts.append('right')
        if (r, c) in s.loc_coords:
            acts.append('enter')
    elif loc == s.locs['cave']:
        return ['kill dragon', 'talk to dragon', ]
    elif loc == s.locs['armory']:
        acts = ['leave']
        wizard = s.agents['wizard']
        if not wizard.been_requested_already:
            acts.append('request enchantment')
        if wizard.alive:
            acts.append('kill wizard')
    else:
        raise Exception(f'Agent in unknown loc: {s.agent.loc}')
    return acts


def R(s, a):
    if not s.agent.alive:
        return -50
    if a == 'enter' and s.agent.loc == s.locs.kingdom and \
            s.locs.victim in s.agent.inventory:
        return 1000
    return 0


def T(s, a):
    if a in ['up', 'down', 'left', 'right']:
        r, c = s.agent.coords
        dr, dc = {'up': (-1, 0), 'down': (1, 0),
                  'left': (0, -1), 'right': (0, 1)}[a]
        s.agent.coords = (r + dr, c + dc)
    if a == 'kill wizard':
        if random() > .5:
            s.actors['wizard'].alive = False
        else:
            s.agent.alive = False
    if a == 'kill king':
        if random() > .7:
            s.actors['king'].alive = False
        else:
            s.agent.alive = False
    if a == 'pick up scroll':
        scroll = s.items['scroll']
        s.locations['swamp'].inventory.pop('scroll')
        s.agent.inventory['scroll'] = scroll
    if a == 'leave':
        s.agent.loc = s.locs['outside_world']
    if a == 'enter':
        assert s.agent.is_at_door()
        s.agent.loc = s.get_loc_by_coords(s.agent.loc)
    return s


def make_intial_state():
    world = World()
    Item.default_owner = world
    knight, king, dragon, wizard = \
        Actor('Knight'), Actor('King'), Actor('Dragon'), Actor('Wizard')
    king.been_asked = False
    wizard.been_asked = False
    actors = [knight, king, dragon, wizard]
    items = [Item('Sword', owner=knight), Item('Enchantment', owner=wizard)]
    locs = [Loc('Swamp', ), Loc('Castle'), Loc('Cave'), Loc('Forge')]
    world = World(actors=actors, items=items, locs=locs)
