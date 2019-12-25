import unittest

from game_engine import *

class Bla(object):
    ''' a simple test class '''
    def __init__(self):
        self.actions = {}

class ActionTests(unittest.TestCase):
    def test_CreateActionWithBadArgs_ThrowsTypeError(self):
        def create_bad_action():
            @Action("test", "t")
            def bad():
                pass
        self.assertRaises(TypeError, create_bad_action)
        
    def test_RegisterAction_ActionIsAvailable(self):
        # ARRANGE
        obj = Bla()

        test_action_names   = ["apple", "beetle", "cat", "dingo"]
        test_action_hotkeys = ["x", "k", "c", "d"]
        test_actions = []

        for name, hotkey in zip(test_action_names, test_action_hotkeys):
            @Action(name, hotkey)
            def test_action(player, room):
                pass
            test_actions.append(test_action)
        
        # ACT
        for action in test_actions:
            register_action(obj, action)

        # ASSERT
        actions = get_all_actions(obj)
        self.assertEqual(len(actions), len(test_actions))
        for test_action in test_actions:
            action = actions[test_action.hotkey]
            self.assertTrue(action.hotkey is test_action.hotkey)
            assert(action is test_action)

    def test_DeregisterAction_ActionDisappears(self):
        # ARRANGE
        obj = Bla()

        test_action_names   = ["apple", "beetle", "cat", "dingo"]
        test_action_hotkeys = ["x", "k", "c", "d"]
        test_actions = []

        for name, hotkey in zip(test_action_names, test_action_hotkeys):
            @Action(name, hotkey)
            def test_action(player, room):
                pass
            test_actions.append(test_action)
        
        for action in test_actions:
            register_action(obj, action)

        # ACT
        action_to_deregister = test_actions.pop()
        deregister_action(obj, action_to_deregister)

        # ASSERT
        actions = get_all_actions(obj)
        self.assertEqual(len(actions), len(test_actions))
        for action in actions:
            self.assertTrue(action is not action_to_deregister)

    def test_deleteAction_actionIsRemovedFromAllOwners(self):
        # ARRANGE
        objs = []
        for i in range(10):
            objs.append(Bla())

        @Action("test", "t")
        def test_action(player, room):
            pass

        @Action("test", "t2")
        def test_action_to_delete(player, room):
            pass

        for obj in objs:
            register_action(obj, test_action)
            register_action(obj, test_action_to_delete)
            self.assertEqual(len(get_all_actions(obj)), 2)
            self.assertTrue(get_all_actions(obj)["t"] is test_action)
            self.assertTrue(get_all_actions(obj)["t2"] is test_action_to_delete)

        # ACT
        delete_action(test_action_to_delete)
        # ASSERT
        for obj in objs:
            self.assertEqual(len(get_all_actions(obj)), 1)
            self.assertTrue(get_all_actions(obj)["t"] is test_action)

        # ACT
        delete_action(test_action)
        # ASSERT
        for obj in objs:
            self.assertEqual(len(get_all_actions(obj)), 0)

class ThingyTests(unittest.TestCase):
    def test_grabThingy_movesFromRoomToPlayer(self):
        # ARRANGE
        room = Bla()
        player = Bla()
        thingy = Thingy("test", "t", noop_action, noop_action)
        register_action(room, thingy.grab)

        self.assertEqual(len(get_all_actions(room)), 1)
        self.assertTrue(get_all_actions(room)['g t'] is thingy.grab)
        self.assertEqual(len(get_all_actions(player)), 0)

        # ACT
        thingy.grab(player, room)

        # ASSERT
        self.assertEqual(len(get_all_actions(room)), 0)
        self.assertEqual(len(get_all_actions(player)), 1)
        self.assertTrue(get_all_actions(player)['d t'] is thingy.drop)


    def test_dropThingy_movesFromPlayerToRoom(self):
        # ARRANGE
        room = Bla()
        player = Bla()
        thingy = Thingy("test", "t", noop_action, noop_action)
        register_action(player, thingy.drop)

        self.assertEqual(len(get_all_actions(room)), 0)
        self.assertEqual(len(get_all_actions(player)), 1)
        self.assertTrue(get_all_actions(player)['d t'] is thingy.drop)

        # ACT
        thingy.drop(player, room)

        # ASSERT
        self.assertEqual(len(get_all_actions(room)), 1)
        self.assertTrue(get_all_actions(room)['g t'] is thingy.grab)
        self.assertEqual(len(get_all_actions(player)), 0)

if __name__ == '__main__':
    unittest.main()
