"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from evennia import utils
from evennia import create_object
from characters import Character

class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    def at_object_creation(self):
        """
        Called only at initial creation. This is a rather silly
        example since ability scores should vary from Character to
        Character and is usually set during some character
        generation step instead.
        """

        # 1 2 3 small medium large
        self.db.roomSize = 0
        # Our rooms will have a title
        self.db.roomTitle = ""
        # eventual modifier for coverage when sneaking/hiding
        self.db.roomCover = 0
        # movement modifier i.e. tarmac v swap for running/driving
        self.db.movementMod = 0
        # Encounter % for zombies
        self.db.zombieEncounter = 10
        # items on searching
        self.db.findItemsChance = 1
        # is the room inside or outside
        self.db.roomInside = 0

    def return_appearance(self, looker):
        """
        This is called when e.g. the look command wants to retrieve
        the description of this object.
        Args:
            looker (Object): The object looking at us.
        Returns:
            description (str): Our description.
        """
        if not looker:
            return ""
            # get and identify all objects
        visible = (con for con in self.contents if con != looker and
                   con.access(looker, "view"))
        exits, users, things = [], [], []
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_player:
                users.append("%s" % key)
            else:
                things.append(key)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            string += "%s" % desc
        if things:
            string += "\n|cYou notice: " + ", ".join(things) + "|n"
        if users:
            string += "\n|MAlso here:|m " + ", ".join(users) + "|n"
        if exits:
            string += "\n|GExits: " + ", ".join(exits)

        return string

    def get_roominfo(self):
        """
        Simple access method to return room abilities
        scores as a tuple (roomSize, roomTitle, roomCover, movementMod, zombieEncounter, findItemsChance)
        """
        return self.db.roomSize, self.db.roomTitle, self.db.roomCover, self.db.movementMod, self.db.zombieEncounter, \
                self.db.findItemsChance

    def at_object_receive(self, obj, source_location):
        if utils.inherits_from(obj, Character):
            # A PC has entered, NPC is caught above.
            # Cause the character to look around
            #
            self.db.findItemsChance = self.db.findItemsChance + 1
            # demonstration
            if self.db.findItemsChance > 10:
                rock = create_object(key="Rock", location=self)
                rock.db.desc = "An ordinary rock."
                self.db.findItemsChance = 1

