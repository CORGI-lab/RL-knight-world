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
import random
from collections import defaultdict
from time import sleep


class SameHashIsSame(object):
    def __eq__(s1, s2):
        return hash(s1) == hash(s2)


class World(SameHashIsSame):
    def __init__(self, actors, items, locs, agent, rows=10, cols=10):
        self.actors = {actor.name: actor for actor in actors}
        self.items = {item.name: item for item in items}
        self.locs = {loc.name: loc for loc in locs}
        self.coords_to_loc = {loc.coords: loc for loc in locs}
        self.agent = agent
        self.rows = rows
        self.cols = cols

    def __repr__(self):
        return f'{self.rows} x {self.cols} world'

    def __hash__(self):
        return hash(((self.rows,
                      self.cols,
                      hash(self.agent),
                      tuple(map(hash, self.actors.values())),
                      tuple(map(hash, self.items.values())),
                      tuple(map(hash, self.locs.values())))))


class Actor(SameHashIsSame):
    def __init__(self, name, loc, items=None, coords=None):
        self.name = name
        self.loc = loc
        loc.actors[name] = self
        self.items = items or dict()
        self.coords = coords
        self.alive = True

    def __repr__(self):
        return f'Actor {self.name}'

    def __hash__(self):
        return hash((self.name,
                     self.loc.name,
                     tuple(i.name for i in self.items.values()),
                     self.coords,
                     self.alive))


class Item(SameHashIsSame):
    default_owner = None

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        owner.items[name] = self

    def __hash__(self):
        return hash((self.name, self.owner.name))

    def __repr__(self):
        return f'Item {self.name}'


class Loc(SameHashIsSame):
    def __init__(self, name, coords, actors=None, items=None):
        self.name = name
        self.coords = coords
        self.actors = actors or dict()
        self.items = items or dict()

    def __hash__(self):
        return hash((self.name,
                     self.coords,
                     tuple(map(hash, self.actors.values()))))

    def __repr__(self):
        return f'Loc {self.name}'


class Agent(Actor):
    pass


def A(s):
    name = s.agent.loc.name
    if name == 'castle':
        acts = ['leave']
        king = s.actors['king']
        if 'sword' in king.items:
            acts.append('ask king')
            acts.append('demand king')
        if king.alive:
            acts.append('kill king')
        return acts
    if name == 'swamp':
        acts = ['leave', 'make dinner', 'enjoy evening']
        if 'scroll' not in s.agent.items:
            acts.append('pick up scroll')
        return acts
    if name == 'outside_world':
        acts = []
        r, c = s.agent.coords
        if r > 0:
            acts.append('up')
        if r < s.rows - 1:
            acts.append('down')
        if c > 0:
            acts.append('left')
        if c < s.cols - 1:
            acts.append('right')
        if (r, c) in s.coords_to_loc:
            acts.append('enter')
        return acts
    if name == 'cave':
        return ['kill dragon', 'talk to dragon', ]
    if name == 'armory':
        acts = ['leave']
        wizard = s.actors['wizard']
        if 'enchantment' in wizard.items:
            acts.append('request enchantment')
        if wizard.alive:
            acts.append('kill wizard')
        return acts
    raise Exception(f'Agent in unknown loc: {s.agent.loc}')


def RT(s, a):
    # Returns reward, is_terminal
    if a in ['up', 'down', 'left', 'right']:
        r, c = s.agent.coords
        dr, dc = {'up': (-1, 0), 'down': (1, 0),
                  'left': (0, -1), 'right': (0, 1)}[a]
        s.agent.coords = (r + dr, c + dc)
        return -1, False
    if a == 'make dinner':
        Item("dinner", s.agent)
        return -1, False
    if a == 'enjoy evening':
        return -1, False
    if a == 'kill wizard':
        if random.random() > .5:
            s.actors['wizard'].alive = False
            return -40, True
        s.agent.alive = False
        return -50, True
    if a == 'kill king':
        if random.random() > .7:
            s.actors['king'].alive = False
            return -40, True
        s.agent.alive = False
        return -50, True
    if a == 'pick up scroll':
        scroll = s.locs['swamp'].items.pop('scroll')
        s.agent.items['scroll'] = scroll
        scroll.owner = s.agent
        return -1, False
    if a == 'leave':
        s.agent.loc = s.locs['outside_world']
        return -1, False
    if a == 'enter':
        s.agent.loc = s.coords_to_loc[s.agent.coords]
        return -1, False
    if a == 'ask king' or a == 'demand king':
        king = s.actors['king']
        assert 'sword' in king.items
        if random.random() > 0.1:
            sword = king.items.pop('sword')
            s.agent['sword'] = sword
            sword.owner = s.agent
        return -1, False
    if a == 'ask wizard' or a == 'demand wizard':
        wizard = s.actors['king']
        assert 'enchantment' in wizard.items
        if random.random() > 0.1:
            enchantment = wizard.items.pop('enchantment')
            s.agent['enchantment'] = enchantment
            enchantment.owner = s.agent
        return -1, False
    raise Exception("Unknown action", a)


def make_initial_state():
    locs = swamp, castle, cave, forge, outside_world = (
        Loc('swamp', (0, 0)), Loc('castle', (2, 3)), Loc('cave', (8, 1)),
        Loc('forge', (5, 5)), Loc('outside_world', None))
    actors = knight, king, dragon, wizard = (
        Actor('knight', cave), Actor('king', castle),
        Actor('dragon', cave), Actor('wizard', forge))
    items = [Item('sword', owner=knight), Item('enchantment', owner=wizard),
             Item('scroll', owner=swamp)]
    agent = Agent("Alice", swamp, None, swamp.coords)
    world = World(actors, items, locs, agent)
    Item.default_owner = world
    return world


# def Q_learning(s0, A, RT, is_terminal, n=100, 𝛼=.2, ε=.05, ɣ=.95):
s0 = make_initial_state()
n = 100
𝛼 = .2
ε = .05
ɣ = .95
Q = defaultdict(int)
S = set()
for _ in range(n):
    s = s0
    h = hash(s)
    while True:
        print("In state", s.agent.coords, s.agent.loc)
        sleep(0.1)
        S.add(h)
        a = (random.choice(A(s))
             if random.random() < ε
             else max(A(s), key=lambda a: Q[h, a]))
        print("Taking action", a)
        sleep(0.1)
        r, is_terminal = RT(s, a)
        print("Received reward", r)
        sleep(0.1)
        h2 = hash(s)
        max_s2 = max(Q[h2, a] for a in A(s))
        Q[h, a] += 𝛼 * (r + ɣ * max_s2 - Q[h, a])
        h = h2
        if is_terminal:
            break
        print()
π = {s: max(A(s), lambda a: Q[s, a])
     for s in S}
