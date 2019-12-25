from inspect import signature

#===================

def make_owned_thing_helpers(name):
    ''' Make a suite of functions used to register
    named `things` in on an object under a member
    dictionary identified by `name` using the
    `hotkey` member of the passed thing.
    '''
    def autovivify(owner):
        ''' it's not my fault, if in God's plan... '''
        if not hasattr(owner, name):
            setattr(owner, name, {})
    def register(owner, thing):
        autovivify(owner)
        getattr(owner, name)[thing.hotkey] = thing
        thing.parents += [owner]
    def deregister(owner, thing):
        if hasattr(owner, name) and thing.hotkey in getattr(owner, name):
            del getattr(owner, name)[thing.hotkey]
    def delete(thing):
        for parent in thing.parents:
            deregister(parent, thing)
    def get(hotkey):
        autovivify(owner)
        return getattr(owner, name)[hotkey]
    def get_all(owner):
        autovivify(owner)
        return getattr(owner, name)
    return register, deregister, delete, get, get_all

#===================

def assertFunctionParamNames(func, name_list):
    ''' Assert that the passed function `func`'s
    parameters have the desired parameter names stored
    in name_list
    '''
    paramError = TypeError("This class requires the "
                        + "following parameters: {}".format(name_list))
    sig = signature(func)
    param_list = list(sig.parameters)
    if len(param_list) != len(name_list):
        raise paramError
    for param, name in zip(param_list, name_list):
        if (param != name):
            raise paramError

def Action(name, hotkey):
    '''Action requires two arguments: name, which is the
    name of the adventure action, and a hotkey, which is
    a short convenience name for the given action.
    '''
    def decorator(func):
        ''' Func should accept two arguments:
        `player`, a `Player` object and `room`, a `Room` object
        '''
        assertFunctionParamNames(func, ["player", "room"])
        func.name = name
        func.hotkey = hotkey
        func.parents = []
        func.desc = "{}: {}".format(hotkey, name)
        return func
    return decorator

register_action, \
deregister_action, \
delete_action, \
get_action, \
get_all_actions = make_owned_thing_helpers("actions")

#===================

class Thingy(object):
    def __init__(self, 
                 name, hotkey, 
                 grab_action, drop_action,
                 room_actions=[], player_actions=[]):
        self.name = name
        self.hotkey = hotkey
        self.room_actions = room_actions
        self.player_actions = player_actions

        grab_name = "grab {}".format(self.name)
        grab_hotkey = "g {}".format(self.hotkey)
        drop_name = "drop {}".format(self.name)
        drop_hotkey = "d {}".format(self.hotkey)

        @Action(grab_name, grab_hotkey)
        def grab(player, room):
            grab_action(player, room)

            deregister_action(room, grab)
            for action in room_actions:
                deregister_action(room, action)

            register_action(player, drop)
            for action in player_actions:
                register_action(player, action)
        self.grab = grab

        @Action(drop_name, drop_hotkey)
        def drop(player, room):
            drop_action(player, room)

            deregister_action(player, drop)
            for action in player_actions:
                deregister_action(player, action)

            register_action(room, grab)
            for action in room_actions:
                register_action(room, action)
        self.drop = drop

        def delete():
            delete_action(grab)
            delete_action(drop)
            for action in room_actions + player_actions:
                delete_action(action)
        self.delete = delete

#===================

class World(object):
    def __init__(self, initial_room, world_action):
        self.initial_room = initial_room
        self.world_action = world_action
        # you can always quit :')
        @Action("Quit", "q")
        def quit(player, room):
            player.victory = True
        register_action(self, quit)
    def act(self, player):
        self.world_action(player)

#===================

def noop(*args):
    pass

@Action("noop", "noop")
def noop_action(player, room):
    pass

def seq(functions):
    def new_fun(*args):
        for fun in functions:
            fun(*args)
    return new_fun

def onetime(fun):
    used=False
    def onetime_fun(*args):
        nonlocal used
        if used == False:
            fun(*args)
            used=True
    return onetime_fun

def make_print_action(phrase):
    def action(player, room):
        print(phrase)
    return action

#===================

class Room(object):
    def __init__(self, name, desc, short_desc, room_action):
        self.name = name
        self.desc = desc
        self.short_desc = short_desc
        self.room_action = room_action
        self.thingies = {}
    def __str__(self):
        desc = ""
        desc += self.desc + "\n"
        for thingy in self.thingies.values():
            desc += thingy.desc + "\n"
        return self.desc
    def act(self, player):
        self.room_action(player)

def link_rooms(room1, room2, passage_phrase, hotkey_pair, action_phrase):
    def make_link_action(newRoom, hotkey):
        @Action("{}, {}".format(passage_phrase, newRoom.short_desc), hotkey)
        def action(player, room):
            print("""
        """ + action_phrase)
            player.room = newRoom
        return action
    a, b = hotkey_pair
    register_action(room1, make_link_action(room2, a))
    register_action(room2, make_link_action(room1, b))

#===================

def increment_stat(player, stat, value):
    if not stat in player.stats:
        player.stats[stat] = 0
    player.stats[stat] += value
    sign = "+" if value >= 0 else ""
    print("""        {}{} {}""".format(sign, value, stat))
def set_stat(player, stat, value):
    player.stats[stat] = value
def get_stat(player, stat):
    if stat in player.stats:
        return player.stats[stat]
    else:
        return 0

def make_stat_incrementer(stat, value):
    @onetime
    def fun(player):
        increment_stat(player, stat, value)
    return fun

#===================

class Player(object):
    def __init__(self):
        self.name = "player"
        self.stats = {}
        self.victory = False #for now (growth mindset)
        self.appearance ="""
        You are wearing a festive sweater sparkling with tinsel.
        You feel real cozy!!!
        """
        @Action("Look at self", "ls")
        def look_at_self(player, room):
            print(self.appearance)
            increment_stat(player, "coziness", 1)

        register_action(self, look_at_self)

    def __str__(self):
        print("""~~ PLAYER STATS ~~""")
        stat_strings = ["{} = {}".format(key, value) 
                        for key, value in self.stats.items()]
        return "\n".join(stat_strings)

