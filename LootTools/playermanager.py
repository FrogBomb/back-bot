from discord import User

class PlayerManager(object):
    def __init__(self):
        """
        A class for managing and updating player names and ids.
        Player key: (<name> : str|None, <id>: int|None)
        """
        self.playerKeys = set()

    def add_name(self, name):
        self.add(name, None)

    def add_id(self, id):
        self.add(None, id)

    def add(self, name, id):
        """Add a new key"""
        key = (name, id)
        if(self._is_a_valid_key(key)):
            self.playerKeys.add(key)
        else:
            raise ValueError

    def add_player(self, player):
        self.add(*(self._soft_try_object_into_key(player)))

    def names(self):
        """List of names"""
        return [n for n, i in self.playerKeys]

    def ids(self):
        """List of ids"""
        return [i for n, i in self.playerKeys]

    def keys(self):
        """List of player keys"""
        return [k for k in self.playerKeys]

    def remove(self, player):
        player_key = self._soft_try_object_into_key(player)
        if(player_key in self.playerKeys):
            self.playerKeys.remove(player_key)

    def __contains__(self, player):
        return len(self[player]) > 0

    def __getitem__(self, player):
        """Get a list of all relevent stored keys"""
        return [k for k in self.genPlayerKeys(player) if k in self.playerKeys]

    def __setitem__(self, player, int_or_str):
        """
        Update all relevent keys
        If int_or_str is an integer, this updates the ids of all matching players.
        If int_or_str is a string, this updates the names.
        """
        if isinstance(int_or_str, int):
            name_set = set()
            for k in self.genPlayerKeys(player):
                if k in self.playerKeys:
                    self.playerKeys.remove(k)
                    name_set.add(k[0])

            for this_name in name_set:
                self.add(this_name, int_or_str)

        elif isinstance(int_or_str, str):
            id_set = set()
            for k in self.genPlayerKeys(player):
                if k in self.playerKeys:
                    self.playerKeys.remove(k)
                    id_set.add(k[1])

            for this_id in id_set:
                self.add(int_or_str, this_id)

            if(len(id_set) > 0):
                if((int_or_str, None) in self.playerKeys):
                    self.playerKeys.remove((int_or_str, None))

        else:
            raise ValueError

    def __delitem__(self, player):
        """Delete all relevent key. (Use remove for single keys)"""
        player = self._soft_try_object_into_key(player)
        for k in [k for k in self.genPlayerKeys(player)]:
            if k in self.playerKeys:
                self.playerKeys.remove(k)

    def _match_keys_value_on_index(self, index_on_key, value):
        no_keys = True
        for k in [k for k in self.playerKeys if k[index_on_key] == value]:
            no_keys = False
            yield k
        if no_keys:
            yield tuple(value if index_on_key == i else None for i in range(2))

    def _is_a_valid_key(self, key):
        return isinstance(key, tuple) and (len(key) == 2) and\
               (isinstance(key[0], str) or key[0] == None) and\
               (isinstance(key[1], int) or key[1] == None)

    def _soft_try_object_into_key(self, player):
        if isinstance(player, User): # Mutate into tuple.
            return (player.name, int(player.id))

        elif isinstance(player, dict): # Mutate into tuple
            return (player['name'], int(player['id']))

        else: # Just pass through otherwise
            return player

    def clearUnknownIds(self):
        for idless_key in [k for k in self.playerKeys if k[1] == None]:
            self.playerKeys.remove(idless_key)

    def genPlayerKeys(self, player = None): #Generate all relevent player keys
        """
        Generator of keys that will match for the input player.

        If the player has an id and name, or is a valid player key,
        this generator will yield all keys with matching ids stored, and
        the (name, id) tuple from the input. (If the id is none, this will just
        match to whatever the name is.)

        If the player is a string, it's assumed to be a name to match to,
        and this will generate all stored names with the given name.
        If there are none, this will generate the tuple (name, None) .

        If the player is an int, it's assumed to be an id to match to,
        and this will generate all stored names with the given id.
        If there are none, this will generate the tuple (None, id) .

        If the player is None, this will simply generate all the stored keys.
        """

        if player == None:
            for k in self.playerKeys:
                yield k
            return

        player = self._soft_try_object_into_key(player)

        if self._is_a_valid_key(player): # name and id tuple
            if(player[1] == None): #Id is none
                for k in self.genPlayerKeys(player[0]):
                    yield k
            else:
                found_player = False
                for k in self.genPlayerKeys(int(player[1])):
                    if k == player:
                        found_player = True
                    yield k

                if(not found_player):
                    yield player

        elif isinstance(player, int): # Assume is id.
            for k in self._match_keys_value_on_index(1, player):
                yield k

        elif isinstance(player, str): # Assume is a name.
            for k in self._match_keys_value_on_index(0, player):
                yield k
        else:
            raise ValueError

def test_player_manager(verbose = False):
    from Helpers.dummyClasses import Dummy_Player

    pm = PlayerManager()
    p_mike = Dummy_Player("Mike", 15)
    p_mike_as_fake_tom = Dummy_Player("Tom", 15)

    if verbose: print("Add Tom, Drew, Robbie and Wendell (no ids)")
    pm.add_name("Tom")
    pm.add_name("Wendell")
    pm.add_name("Drew")
    pm.add_name("Robbie")
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Drew', None), ('Robbie', None), ('Wendell', None), ('Tom', None)}

    if verbose: print("Just give Tom the Id 12")
    pm["Tom"] = 12
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Tom', 12), ('Drew', None), ('Robbie', None), ('Wendell', None)}

    if verbose: print("Add a nameless Id 14")
    pm.add_id(14)
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Tom', 12), ('Drew', None), ('Robbie', None), ('Wendell', None), (None, 14)}

    if verbose: print("Mike with id 15 is masking Tom's name")
    pm.add_player(p_mike)
    pm.add_player(p_mike_as_fake_tom)
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Tom', 12), ('Tom', 15), ('Mike', 15),\
         ('Robbie', None), ('Wendell', None), (None, 14), ('Drew', None)}


    if verbose: print("Id 14 is found! It's Robbie")
    pm[14] = "Robbie"
    assert set(k for k in pm.genPlayerKeys()) == \
          {('Tom', 12), ('Tom', 15), ('Mike', 15), ('Robbie', 14),\
           ('Wendell', None), ('Drew', None)}


    if verbose: print("Wendell's id is found (13)")
    pm["Wendell"] = 13
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Tom', 12), ('Tom', 15), ('Mike', 15), ('Wendell', 13),\
         ('Robbie', 14), ('Drew', None)}

    if verbose: print("Tom has a new name! notTom" )
    pm.add("notTom", 12)
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Tom', 12), ('Tom', 15), ('Mike', 15),\
         ('Wendell', 13), ('Robbie', 14), ('Drew', None), ('notTom', 12)}

    if verbose: print("Keys associated with Id's with the name Wendell")
    assert set(k for w in pm["Wendell"] for k in pm[w[1]]) == {('Wendell', 13)}

    if verbose: print("Keys associated with Id's with the name Tom.")
    assert set(k for w in pm["Tom"] for k in pm[w[1]]) == \
        {('Tom', 12), ('notTom', 12), ('Tom', 15), ('Mike', 15)}

    if verbose: print("Remove the name masking Mike did on Tom, and see the last thing again")
    pm.remove(("Tom", 15))
    assert set(k for w in pm["Tom"] for k in pm[w[1]]) == \
        {('Tom', 12), ('notTom', 12)}

    if verbose: print("Mike masked Tom again.")
    pm.add("Tom", 15)
    assert set(k for w in pm["Tom"] for k in pm[w[1]]) == \
        {('Tom', 12), ('notTom', 12), ('Tom', 15), ('Mike', 15)}

    if verbose: print("Now, delete Mike")
    del pm[p_mike]
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Robbie', 14), ('Tom', 12), ('Drew', None), ('Wendell', 13), ('notTom', 12)}

    if verbose: print("Remove None ids")
    pm.clearUnknownIds()
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Robbie', 14), ('Tom', 12), ('Wendell', 13), ('notTom', 12)}

    if verbose: print("Now, delete Tom by Id")
    del pm[12]
    assert set(k for k in pm.genPlayerKeys()) == \
        {('Robbie', 14), ('Wendell', 13)}
