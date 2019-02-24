"""
A markov decision process and a q learning agent
Luke Harold Miles, January 2019
"""

import random
from collections import defaultdict
from time import sleep

import narrative_tree

subtree = narrative_tree.tree


class World():
    """
    The whole world, including all actors, items, locations, and the agent.
    Is hashed to create a single state for the MDP.
    """

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.actors = dict()
        self.locs = dict()
        self.items = dict()
        self.coords_to_loc = dict()
        self.agent = None

    def __repr__(self):
        return f'{self.rows} x {self.cols} world'

    def __hash__(self):
        return hash((self.agent, tuple(self.actors.values()),
                     tuple(self.items.values())))


class Agent():
    """
    The agent in the environment
    """

    def __init__(self, world, loc, coords):
        world.agent = self
        self.name = 'Agent'
        self.loc = loc
        self.coords = coords
        self.alive = True

    def __repr__(self):
        return f'The agent'

    def __hash__(self):
        return hash((self.loc.name, self.coords, self.alive))


class Actor():
    """
    A non-agent actor in the world, such as the wizard
    """

    def __init__(self, world, name, loc):
        world.actors[name] = self
        self.name = name
        self.loc = loc
        self.alive = True

    def __repr__(self):
        return f'Actor {self.name}'

    def __hash__(self):
        return hash((self.name, self.alive))


class Item():
    """
    An item, such as a sword
    """

    def __init__(self, world, name, owner):
        world.items[name] = self
        self.name = name
        self.owner = owner

    def __repr__(self):
        return f'Item {self.name}'

    def __hash__(self):
        return hash((self.name, self.owner.name))


class Loc():
    """
    A location, such as the swamp
    """

    def __init__(self, world, name, coords=None):
        world.locs[name] = self
        world.coords_to_loc[coords] = self
        self.name = name
        self.coords = coords

    def __repr__(self):
        return f'{self.name}'


def A(s):
    """
    Input: a state
    Output: the set of possible actions
    """
    name = s.agent.loc.name

    acts = ['wait']

    if name != 'outside':
        acts.append(f'leave {name}')

    if name == 'swamp':
        acts.append('enjoy evening')
        if s.items['dinner'].owner is s.locs['swamp']:
            acts.append('make dinner')
        if s.items['scroll'].owner is s.locs['swamp']:
            acts.append('pick up scroll')
        return acts

    if name == 'kingdom':
        king = s.actors['king']
        if s.items['slip'].owner is king:
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
        acts.extend(['kill dragon', 'talk to dragon'])
        return acts

    if name == 'forge':
        blacksmith = s.actors['blacksmith']
        if blacksmith.alive:
            acts.append('kill blacksmith')
            if s.items['sword'].owner is blacksmith:
                acts.append('ask blacksmith for sword')
            if s.items['slip'].owner is s.agent:
                acts.append('give blacksmith slip from king')
        if s.items['sword'].owner is blacksmith:
            acts.append('steal sword')
        return acts

    if name == 'tower':
        wizard = s.actors['wizard']
        if s.items['amulet'].owner is wizard:
            acts.append('steal amulet')
            if wizard.alive:
                acts.extend(('ask wizard for amulet',
                             'demand wizard for amulet'))
        if wizard.alive:
            acts.append('kill wizard')
        return acts

    if name == 'tavern':
        acts.extend(['eat pizza', 'play pacman'])
        return acts

    if name == 'outside':
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
            acts.append(f'go to {s.coords_to_loc[r, c].name}')
        return acts

    raise Exception(f'Agent in unknown loc: {s.agent.loc}')


def RT(s, a):
    """
    Input: state s, action a
    Output: reward, is_terminal
    Side effect: transitions the state
    """
    global subtree
    name = s.agent.loc.name

    if a in subtree:
        reward = 50 * (narrative_tree.scores[a] - 0.5)
        subtree = subtree[a]
    else:
        reward = 0

    # some actions are location-independent:

    if a == 'wait':  # do nothing
        return reward + -1, False

    if a.startswith('leave'):
        s.agent.loc = s.locs['outside']
        return reward + -1, False

    if a.startswith('go to'):
        s.agent.loc = s.coords_to_loc[s.agent.coords]
        return reward + -1, False

    # most actions depend on location:

    if name == 'swamp':
        if a == 'make dinner':
            s.items['dinner'].owner = s.agent
            return reward + -1, False
        if a == 'enjoy evening':
            # does nothing
            return reward + -1, False
        if a == 'pick up scroll':
            s.items['scroll'].owner = s.agent
            return reward + -1, False

    if name == 'kingdom':
        king = s.actors['king']
        if a == 'ask king for slip' or a == 'demand king for slip':
            if random.random() > 0.1:
                s.items['slip'].owner = s.agent
            return reward + -1, False
        if a == 'kill king':
            if s.items['sword'].owner == s.items['amulet'].owner == s.agent:
                king.alive = False
                return reward + -1, False
            if s.items['sword'].owner is s.agent and random.random() < 0.8:
                king.alive = False
                return reward + -1, False
            return reward + -10, True  # you die
        if a == 'chat with pleb1':
            return reward + -1, False
        if a == 'kill pleb1':
            pleb1 = s.actors['pleb1']
            pleb1.alive = False
            return reward + -1, False

    if name == 'cave':
        if a == 'kill dragon':
            dragon = s.actors['dragon']
            if s.items['sword'].owner == s.items['amulet'].owner == s.agent:
                dragon.alive = False
                return reward + 100, True
            #if 'sword' in items and random.random() < 0.1:
            #    dragon.alive = False
            #    return reward + 100, True
            return reward + -10, True  # you die
        if a == 'talk to dragon':
            return reward + -10, True  # you die

    if name == 'forge':
        blacksmith = s.actors['blacksmith']
        if a == 'give blacksmith slip from king':
            s.items['slip'].owner = blacksmith
            return reward + -1, False
        if a == 'kill blacksmith':
            blacksmith.alive = False
            return reward + -1, False
        if a == 'steal sword':
            # can only steal sword if you kill the blacksmith
            if not blacksmith.alive:
                s.items['sword'].owner = s.agent
            return reward + -1, False
        if a == 'ask blacksmith for sword':  # yay!
            if s.items['slip'].owner == blacksmith:
                s.items['sword'].owner = s.agent
            return reward + -1, False

    if name == 'tower':
        # wizard is less tough, can be stolen from without murder
        wizard = s.actors['wizard']
        if a in [
                'ask wizard for amulet', 'demand wizard for amulet',
                'steal amulet'
        ]:
            s.items['amulet'].owner = s.agent
            return reward + -1, False
        if a == 'kill wizard':
            wizard.alive = False
            return reward + -1, False

    if name == 'tavern':
        # A very simple goal to test Q-learning:
        # if a == 'eat pizza':
        #     return reward + 100, True
        return reward + -1, False  # nothing matters

    if name == 'outside':
        if a in ['up', 'down', 'left', 'right']:
            r, c = s.agent.coords
            dr, dc = {
                'up': (-1, 0),
                'down': (1, 0),
                'left': (0, -1),
                'right': (0, 1)
            }[a]
            s.agent.coords = (r + dr, c + dc)
            return reward + -1, False

    raise Exception(f'Invalid action {a} in state {s}')


def make_initial_state():
    """
    Create the starting state for the MDP
    """
    world = World(10, 10)
    swamp, kingdom, cave, forge, tower, _, _ = \
        [Loc(world, name, coords) for name, coords in [
            ['swamp', (0, 0)],
            ['kingdom', (2, 3)],
            ['cave', (8, 1)],
            ['forge', (5, 5)],
            ['tower', (1, 2)],
            ['tavern', (1, 1)],
            ['outside', None]]]
    actors = king, _, _, blacksmith, wizard = \
        [Actor(world, name, loc) for name, loc in [
            ['king', kingdom],
            ['pleb1', kingdom],
            ['dragon', cave],
            ['blacksmith', forge],
            ['wizard', tower]]]
    items = \
        [Item(world, name, owner) for name, owner in [
            ['scroll', swamp],
            ['slip', king],
            ['dinner', swamp],
            ['sword', blacksmith],
            ['amulet', wizard]]]
    Agent(world, swamp, swamp.coords)
    return world


#if __name__ == '__main__':
def play_game():
    """
    Interactively take actions and observe rewards
    """
    s = make_initial_state()
    is_terminal = False
    while not is_terminal:
        print()
        print('In state', s)
        actions = A(s)
        while True:
            print('Choices:')
            for i, a in enumerate(actions):
                print(i, ':', a)
            choice = input('Choose action: ')
            if choice.isdigit() and 0 <= int(choice) < len(actions):
                break
            if choice == 'e':  # for execute
                code = input('Enter code: ')
                exec(code)
        print('Taking action:', actions[int(choice)])
        reward, is_terminal = RT(s, actions[int(choice)])
        print('Received reward', reward)
        print('Current hash is', hash(s))


#def q_learning():
if __name__ == '__main__':
    """
    Perform Q learning.
    a: action
    r: reward
    s: state
    """
    Q = defaultdict(int)  # Q-values
    total_time = 0
    debug = False
    num_episodes = 100001
    learning_rate = .0 if debug else .2
    chance_of_random_move = .0 if debug else .05
    discount_factor = .99
    for episode in range(num_episodes):
        subtree = narrative_tree.tree  # put us at the start of the story
        timestep = 0
        s = make_initial_state()
        h = hash(s)
        if debug or episode % 100 == 0:
            print(f'EPISODE {episode}')
        while True:
            if debug: sleep(1.5)
            timestep += 1
            total_time += 1
            a = (random.choice(A(s)) if random.random() < chance_of_random_move
                 else max(A(s), key=lambda a: Q[h, a]))
            r, is_terminal = RT(s, a)
            h2 = hash(s)
            if debug:
                print()
                print('Timestep:', timestep)
                print('Action:', a)
                print('Reward:', r)
                print('Location:', s.agent.loc)
                print('Coordinates:', s.agent.coords)
                print('Hash:', h2)
            max_s2 = max(Q[h2, a] for a in A(s))
            Q[h, a] += learning_rate * (r + discount_factor * max_s2 - Q[h, a])
            h = h2
            if is_terminal:
                break
