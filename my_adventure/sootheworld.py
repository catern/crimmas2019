from game_engine import *

###### Foyer ######
foyer = Room("Foyer", """
You find yourself in a soothing foyer with soft, warm light, and clean
pine-scented air. Simple chimes are playing softly.  The walls are
wood and fresh towels are folded in a corner.

There's a notice on the wall that reads:
"REACH PRESENT THROUGH SOOTHIOLENCE"
""",
             "you hear faint chimes...",
             make_stat_incrementer("soothed", 2))

@Action("Take towel", "tw")
def take_towel(player, room):
    if get_stat(player, "towels") > 1:
        print("""
You take a towel and balance it on your head, on top of your other towels.""")
    elif get_stat(player, "towels") == 1:
        print("""
You take a towel and balance it on your head, on top of your other towel.""")
    else:
        print("""
You take a towel and balance it on your head.""")
    increment_stat(player, "towels", 1)
register_action(foyer, take_towel)

###### Teahouse ######
teahouse = Room("Tea House", """
There's a hearth with a pot of boiling water over it, and plenty of
leaves for tea.

There's a table with two mugs on it.
""",
                "you smell fresh tea...",
                make_stat_incrementer("soothed", 1))

link_rooms(foyer, teahouse, "Through a small square door", ("n", "s"),
           "You duck through the door...")

@Action("Brew some tea", "t")
def brew_tea(player, room):
    print("""
You brew some tea in one of the mugs, and drink it up. Ahh....""")
    increment_stat(player, "soothed", 3)
    increment_stat(player, "slaked", 1)
register_action(teahouse, brew_tea)

###### Onsen ######
def onsen_action(player):
    if get_stat(player, "towels") > 0:
        print("""
You enter the onsen - you have the required towel.

The spring is warm and the hot water soothes you to your very soul.
The sound and sight of the water flowing over the rocks is beautiful,
too.

In one part of the onsen, you see some monkeys bathing. It seems a
strange place for a monkey.

When you emerge from the spring, you use your towel to dry off,
and put it in the laundry barrel.
""")
        increment_stat(player, "soothed", 7)
        increment_stat(player, "towels", -1)
    else:
        print("""
You enter the onsen zone, and consider getting in the spring...
but some force causes you to remember...
you're missing something!

You don't feel right going any further without that thing you're missing.
It's a little un-soothing.
        """)
        increment_stat(player, "soothed", -(1/16))

onsen = Room("Onsen", "",
             "you feel a humid heat...",
             onsen_action)

link_rooms(foyer, onsen, "Through a stone arch", ("e", "w"),
           "You pad beneath the arch...")

###### Massage room ######
massage_room = Room("", """
There's just a table in this room, with what looks like a headrest.
It must be a massage table, but there's no-one around.

There's a massagey stick with little fingeys on it, though.
""",
             "you see movement against the light...",
             make_stat_incrementer("soothed", 0))

link_rooms(foyer, massage_room, "Through some hanging beads", ("w", "e"),
           "You gently push aside some beads and move through...")

@Action("Use fingeystick", "u f")
def use_stick(player, room):
    print("""
You rub your back with the massage stick with little fingeys. It's
mildly soothing.
""")
    increment_stat(player, "soothed", .5)
register_action(massage_room, use_stick)


@Action("Rest on table", "r t")
def rest_on_table(player, room):
    print("""
You rest on the table, face-down. It's pretty soothing all on its own,
even without someone to massage you!
""")
    increment_stat(player, "soothed", 2)
register_action(massage_room, rest_on_table)

# =====

class OneTimeConditionalAction(object):
    def __init__(self, action, condition):
        self.action = action
        self.condition = condition
    @onetime 
    def register(self, obj):
        register_action(obj, self.action)
    def check(self, player):
        if self.condition(player):
            self.register(player)

@Action("Attain Present", "ap")
def apotheosis_action(player, room):
    print("""
A golden light wreathes you, and your vision blurs.
You feel a tremendous energy coursing through you-
the power of A PRESENT!!!

You are so soothed,
that you attain knowledge of your present:
You can become soothed in REAL LIFE,
with the aid of a REAL LIFE MASSAGE APPOINTMENT,
at a REAL LIFE SPA!
(Scheduling pending on your convenience)
        """)
    increment_stat(player, "soothed", 998832419875)
    delete_action(apotheosis_action)
def apotheosis_check(player):
    return get_stat(player, "soothed") > 15
apotheosis = OneTimeConditionalAction(apotheosis_action, apotheosis_check)

def world():
    conditions = [apotheosis]
    def world_action(player):
        nonlocal conditions
        for condition in conditions:
            condition.check(player)

    return World(foyer, world_action)

def player():
    player = Player();
    set_stat(player, "soothed", 1)
    return Player()

if __name__ == "__main__":
    import mainloop
    my_world = world()
    my_player = player()
    my_player.room = my_world.initial_room
    my_player.appearance = """
You sing a love song and feel cozy. 'w'"""
    mainloop.play(my_player, my_world, mainloop.interactive_choose)
