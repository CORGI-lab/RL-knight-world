# Structure:
# One state is the entire world.
# The world contains actors, items, and locs, which are all objects.
# Only the agent can take actions. Actions are strings.
#  Most actions are deterministic.
import random
from collections import defaultdict
from time import sleep

sleep_time = 0.0
print_interval = 10000


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

    if name == 'swamp':
        acts = ['leave', 'enjoy evening']
        if 'dinner' not in s.agent.items:
            acts.append('make dinner')
        if 'scroll' not in s.agent.items:
            acts.append('pick up scroll')
        return acts

    if name == 'kingdom':
        acts = ['leave']
        king = s.actors['king']
        if 'slip' in king.items:
            acts.append('ask king for slip')
            acts.append('demand king for slip')
        if king.alive:
            acts.append('kill king')
        pleb1 = s.actors['pleb1']
        if pleb1.alive:
            acts.append('kill pleb1')
            acts.append('chat with pleb1')
        return acts

    if name == 'cave':
        return ['kill dragon', 'talk to dragon', 'leave']

    if name == 'forge':
        acts = ['leave']
        blacksmith = s.actors['blacksmith']
        if blacksmith.alive:
            acts.append('kill blacksmith')
            if 'sword' in blacksmith.items:
                acts.append('ask for sword')
            if 'slip' in s.agent.items:
                acts.append('give blacksmith slip from king')
        if 'sword' in blacksmith.items:
            acts.append('steal sword')
        return acts

    if name == 'tower':
        acts = ['leave']
        wizard = s.actors['wizard']
        if 'amulet' in wizard.items:
            acts.append('steal amulet')
            if wizard.alive:
                acts.extend(('ask wizard for amulet',
                             'demand wizard for amulet'))
        if wizard.alive:
            acts.append('kill wizard')
        return acts

    if name == 'tavern':
        return ['leave', 'eat pizza', 'play pacman']

    if name == 'outside':
        acts = ['wait']
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

    raise Exception(f'Agent in unknown loc: {s.agent.loc}')


def transfer(item_name, old, new):
    item = old.items.pop(item_name)
    new.items[item_name] = item
    item.owner = new


def RT(s, a):
    'Returns reward, is_terminal'
    name = s.agent.loc.name

    # some actions are location-independent:

    if a == 'leave':
        s.agent.loc = s.locs['outside']
        return -1, False

    if a == 'enter':
        s.agent.loc = s.coords_to_loc[s.agent.coords]
        return -1, False

    # most actions depend on location:

    if name == 'swamp':
        if a == 'make dinner':
            Item('dinner', s.agent)
            return -1, False
        if a == 'enjoy evening':
            # does nothing
            return -1, False
        if a == 'pick up scroll':
            transfer('scroll', s.locs['swamp'], s.agent)
            return -1, False

    if name == 'kingdom':
        king = s.actors['king']
        if a == 'ask king for slip' or a == 'demand king for slip':
            if random.random() > 0.1:
                transfer('slip', king, s.agent)
            return -1, False
        if a == 'kill king':
            items = s.agent.items
            if 'sword' in items and 'amulet' in items:
                king.alive = False
                return -1, False
            if 'sword' in items and random.random() < 0.8:
                king.alive = False
                return -1, False
            return -100, True  # you die
        if a == 'chat with pleb1':
            return -1, False
        if a == 'kill pleb1':
            pleb1 = s.actors['pleb1']
            pleb1.alive = False
            return -1, False

    if name == 'cave':
        if a == 'kill dragon':
            items = s.agent.items
            dragon = s.actors['dragon']
            if 'sword' in items and 'amulet' in items:
                dragon.alive = False
                return 1000, True
            if 'sword' in items and random.random() < 0.1:
                dragon.alive = False
                return 1000, True
            return -100, True  # you die
        if a == 'talk to dragon':
            return -100, True  # you die

    if name == 'forge':
        blacksmith = s.actors['blacksmith']
        if a == 'give blacksmith slip from king':
            transfer('slip', s.agent, blacksmith)
            return -1, False
        if a == 'kill blacksmith':
            blacksmith.alive = False
            return -1, False
        if a == 'steal sword':
            # can only steal sword if you kill the blacksmith
            if not blacksmith.alive:
                transfer('sword', blacksmith, s.agent)
            return -1, False
        if a == 'ask for sword':  # yay!
            if 'slip' in blacksmith.items:
                transfer('sword', blacksmith, s.agent)
            return -1, False

    if name == 'tower':
        # wizard is less tough, can be stolen from without murder
        wizard = s.actors['wizard']
        if a in ['ask wizard for amulet',
                 'demand wizard for amulet',
                 'steal amulet']:
            transfer('amulet', wizard, s.agent)
            return -1, False
        if a == 'kill wizard':
            wizard.alive = False
            return -1, False

    if name == 'tavern':
        # if a == 'eat pizza':  # NOTE: REMOVE THIS
        #     return 1000, True  # NOTE: JUST TO TEST Q-LEARNING
        return -1, False  # nothing matters

    if name == 'outside':
        if a == 'wait':
            return -1, False
        if a in ['up', 'down', 'left', 'right']:
            r, c = s.agent.coords
            dr, dc = {'up': (-1, 0), 'down': (1, 0),
                      'left': (0, -1), 'right': (0, 1)}[a]
            s.agent.coords = (r + dr, c + dc)
            return -1, False

    raise Exception(f'Invalid action {a} in state {s}')


def make_initial_state():
    locs = swamp, kingdom, cave, forge, tower, tavern, outside = \
        [Loc(name, coords) for name, coords in [
            ['swamp', (0, 0)],
            ['kingdom', (2, 3)],
            ['cave', (8, 1)],
            ['forge', (5, 5)],
            ['tower', (1, 2)],
            ['tavern', (1, 1)],
            ['outside', None]]]
    actors = king, _, __, blacksmith, wizard = \
        [Actor(name, loc) for name, loc in [
            ['king', kingdom],
            ['pleb1', kingdom],
            ['dragon', cave],
            ['blacksmith', forge],
            ['wizard', tower],
        ]]
    items = \
        [Item(name, owner=owner) for name, owner in [
            ['scroll', swamp],
            ['slip', king],
            ['sword', blacksmith],
            ['amulet', wizard]]]
    agent = Agent('Alice', swamp, None, swamp.coords)
    world = World(actors, items, locs, agent)
    Item.default_owner = world
    return world


# def Q_learning(s0, A, RT, is_terminal, n=100, 𝛼=.2, ε=.05, ɣ=.95):
# def Q_learning():
n = 10000
𝛼 = .2
ε = .05
ɣ = .95
Q = defaultdict(int)
S = set()
i = 0
for _ in range(n):
    s = make_initial_state()
    h = hash(s)
    while True:
        i += 1
        if i % print_interval == 0:
            print(i)
            print('In state', s.agent.coords, s.agent.loc)
        sleep(sleep_time)
        S.add(h)
        a = (random.choice(A(s))
             if random.random() < ε
             else max(A(s), key=lambda a: Q[h, a]))
        if i % print_interval == 0:
            print('Taking action', a)
        sleep(sleep_time)
        r, is_terminal = RT(s, a)
        if i % print_interval == 0 or r != -1:
            print(f'Action {a} got reward {r}')
        sleep(sleep_time)
        h2 = hash(s)
        max_s2 = max(Q[h2, a] for a in A(s))
        Q[h, a] += 𝛼 * (r + ɣ * max_s2 - Q[h, a])
        h = h2
        if is_terminal:
            break
        if i % print_interval == 0:
            print()


def π(s):
    return max(A(s), lambda a: Q[s, a])


# return π


def play_game():
    s = make_initial_state()
    is_terminal = False
    while not is_terminal:
        print("In state", s)
        actions = A(s)
        while True:
            print("Choices:")
            for i, a in enumerate(actions):
                print(i, ':', a)
            choice = input("Choose action: ")
            if choice.isdigit() and 0 <= int(choice) < len(actions):
                break
            if choice == 'e':  # for execute
                code = input("Enter code: ")
                exec(code)
        print("Taking action:", actions[int(choice)])
        reward, is_terminal = RT(s, actions[int(choice)])
        print("Received reward", reward)
