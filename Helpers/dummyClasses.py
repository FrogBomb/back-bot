from discord import User
class Dummy_Player(User):
        def __init__(self, name = None, id = None):
            self.id = id
            self.name = name
