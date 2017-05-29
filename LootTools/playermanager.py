from discord import User

class PlayerManager(object):
    def __init__(self):
        """
        A class for managing and updating player names and ids.
        Player key: (<name> : str|None, <id>: int|None)
        """
        self.playerKeys = []

    def add(self, key):
        """Add a new key"""
        if(self._is_a_valid_key(key)):
            self.playerKeys.append(key)
        else:
            raise ValueError

    def names(self):
        """List of names"""
        return [n for n, i in self.playerKeys]

    def ids(self):
        """List of ids"""
        return [i for n, i in self.playerKeys]

    def keys(self):
        """List of player keys"""
        return [k for k in self.playerKeys]

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
        if isinstance(key_like, int):
            name_set = set()
            for k in self.genPlayerKeys(player):
                if k in self.playerKeys:
                    self.playerKeys.remove(k)
                    name_set.add(k[0])
            for this_name in name_set:
                self.add((this_name, key_like))

        elif isinstance(key_like, str):
            id_set = set()
            for k in self.genPlayerKeys(player):
                if k in self.playerKeys:
                    self.playerKeys.remove(k)
                    id_set.add(k[1])

            for this_id in id_set:
                self.add((key_like, this_id))

        else:
            raise ValueError

    def __delitem__(self, player):
        """Delete all relevent keys"""
        for k in self.genPlayerKeys(player):
            if k in self.playerKeys:
                self.playerKeys.remove(k)

    def _match_keys_value_on_index(self, index_on_key, value):
        no_keys = True
        for k in [k for k in self.playerKeys if k[index_on_key] == player]:
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
