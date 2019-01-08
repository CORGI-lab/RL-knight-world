'''
A markov decision process and a q learning agent
Luke Harold Miles, December 2018
'''

import random
from collections import defaultdict
from time import sleep

import narrative_tree

subtree = narrative_tree.tree


class World():
    '''
    The whole world, including all actors, items, locations, and the agent.
    Is hashed to create a single state for the MDP.
    '''
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
        return hash((self.agent, tuple(self.actors.values())))


class Actor():
    '''
    A non-agent actor in the world, such as the wizard
    '''
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
        return hash((self.name, self.loc.name, self.coords, self.alive,
                     tuple(self.items.keys())))


class Item():
    '''
    An item, such as a sword
    '''
    default_owner = None

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        owner.items[name] = self

    def __repr__(self):
        return f'Item {self.name}'


class Loc():
    '''
    A location, such as the swamp
    '''
    def __init__(self, name, coords, actors=None, items=None):
        self.name = name
        self.coords = coords
        self.actors = actors or dict()
        self.items = items or dict()

    def __repr__(self):
        return f'{self.name}'


class Agent(Actor):
    '''
    The Q-learning agent
    '''
    pass


def A(s):
    '''
    Input: a state
    Output: the set of possible actions
    '''
    name = s.agent.loc.name

    acts = ['wait']

    if name != 'outside':
        acts.append(f'leave {name}')

    if name == 'swamp':
        acts.append('enjoy evening')
        if 'dinner' not in s.agent.items:
            acts.append('make dinner')
        if 'scroll' not in s.agent.items:
            acts.append('pick up scroll')
        return acts

    if name == 'kingdom':
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
        acts.extend(['kill dragon', 'talk to dragon'])
        return acts

    if name == 'forge':
        blacksmith = s.actors['blacksmith']
        if blacksmith.alive:
            acts.append('kill blacksmith')
            if 'sword' in blacksmith.items:
                acts.append('ask blacksmith for sword')
            if 'slip' in s.agent.items:
                acts.append('give blacksmith slip from king')
        if 'sword' in blacksmith.items:
            acts.append('steal sword')
        return acts

    if name == 'tower':
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


def transfer(item_name, old, new):
    '''
    Input: item to transfer, old owner, and new owner
    Side effect: the item is transferred
    '''
    item = old.items.pop(item_name)
    new.items[item_name] = item
    item.owner = new


def RT(s, a):
    '''
    Input: state s, action a
    Output: reward, is_terminal
    Side effect: transitions the state
    '''
    global subtree
    name = s.agent.loc.name

    if a in subtree:
        reward = 50 * (narrative_tree.scores[a] - 0.5)
        subtree = subtree[a]
    else:
        reward = 0

    # some actions are location-independent:

    if a == 'wait': # do nothing
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
            Item('dinner', s.agent)
            return reward + -1, False
        if a == 'enjoy evening':
            # does nothing
            return reward + -1, False
        if a == 'pick up scroll':
            transfer('scroll', s.locs['swamp'], s.agent)
            return reward + -1, False

    if name == 'kingdom':
        king = s.actors['king']
        if a == 'ask king for slip' or a == 'demand king for slip':
            if random.random() > 0.1:
                transfer('slip', king, s.agent)
            return reward + -1, False
        if a == 'kill king':
            items = s.agent.items
            if 'sword' in items and 'amulet' in items:
                king.alive = False
                return reward + -1, False
            if 'sword' in items and random.random() < 0.8:
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
            items = s.agent.items
            dragon = s.actors['dragon']
            if 'sword' in items and 'amulet' in items:
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
            transfer('slip', s.agent, blacksmith)
            return reward + -1, False
        if a == 'kill blacksmith':
            blacksmith.alive = False
            return reward + -1, False
        if a == 'steal sword':
            # can only steal sword if you kill the blacksmith
            if not blacksmith.alive:
                transfer('sword', blacksmith, s.agent)
            return reward + -1, False
        if a == 'ask blacksmith for sword':  # yay!
            if 'slip' in blacksmith.items:
                transfer('sword', blacksmith, s.agent)
            return reward + -1, False

    if name == 'tower':
        # wizard is less tough, can be stolen from without murder
        wizard = s.actors['wizard']
        if a in ['ask wizard for amulet',
                 'demand wizard for amulet',
                 'steal amulet']:
            transfer('amulet', wizard, s.agent)
            return reward + -1, False
        if a == 'kill wizard':
            wizard.alive = False
            return reward + -1, False

    if name == 'tavern':
        # if a == 'eat pizza':  # NOTE: REMOVE THIS
        #     return reward + 100, True  # NOTE: JUST TO TEST Q-LEARNING
        return reward + -1, False  # nothing matters

    if name == 'outside':
        if a in ['up', 'down', 'left', 'right']:
            r, c = s.agent.coords
            dr, dc = {'up': (-1, 0), 'down': (1, 0),
                      'left': (0, -1), 'right': (0, 1)}[a]
            s.agent.coords = (r + dr, c + dc)
            return reward + -1, False

    raise Exception(f'Invalid action {a} in state {s}')


def make_initial_state():
    '''
    Create the starting state for the MDP
    '''
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

#if __name__ == '__main__':
def play_game():
    '''
    Interactively take actions and observe rewards
    '''
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
    '''
    Perform Q learning. Done in the global scope so that variables are
    easier to inspect and modify.
    a: action
    r: reward
    s: state
    '''
    Q = defaultdict(int) # Q-values
    total_time = 0
    debug = True
    num_episodes = 100001
    learning_rate = .0 if debug else .2
    chance_of_random_move = .0 if debug else .05
    discount_factor = .99
    for episode in range(num_episodes):
        subtree = narrative_tree.tree # put us at the start of the story
        timestep = 0
        s = make_initial_state()
        h = hash(s)
        if debug or episode % 100 == 0:
            print(f'EPISODE {episode}')
        while True:
            if debug: sleep(1.5)
            timestep += 1
            total_time += 1
            a = (random.choice(A(s))
                 if random.random() < chance_of_random_move
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

