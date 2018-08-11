"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from world import rules
from typeclasses.items import Clothing
from world.rules_inventory import ClothingSlots

class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(player) -  when Player disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Player has disconnected"
                    to the room.
    at_pre_puppet - Just before Player re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "PlayerName has entered the game" to the room.

    """
    def at_object_creation(self):
        """
        Called only at initial creation.


        """
        #set persistent attributes

        # Base attributes
        self.db.attr_strength = 1
        self.db.attr_agility = 1
        self.db.attr_intelligence = 1
        self.db.attr_constitution = 1
        self.db.attr_perception = 1


        # Hitpoints
        self.db.stat_hitpoints = 30
        self.db.stat_hitpoints_current = 10
        # Contagion level - Min 5, everyone is affected
        self.db.stat_contagion = 5
        # Movement
        self.db.stat_energy = 20
        self.db.stat_energy_current = 20


        # defence
        #   Defense Stats can get updated when we equip/wear items
        # Defense versus grapple from zombies, people doing judo on you etc.
        self.db.stat_defence_unarmed = 1

        # Zombie attacks rely on coverage/ability to stop being eaton
        # Maybe a factor of Percentage coverage and how good the coverage is of clothes/armour
        #   i.e. if every slot is covered
        self.db.stat_defence_zombie = 2

        # Defense versus hand to hand weapons
        self.db.stat_defence_physical = 3

        # Penetration - high velocity weapons - arrows, bullets, spears, gings etc.
        self.db.stat_defence_penetration = 4

        # Max = what they can carry in total (weight?)
        self.db.stat_encumbrance_max = 100
        # Now = what there actually carrying - we'll update when they pickup/drop items
        self.db.stat_encumbrance_now = 10

        # Need to work out default skills
        #   Character must "have" a skill to use it
        #   Skills will be commands
        #   They will take a character and other objects to run success/actions etc.
        #   e.g. sneak - Character Stealth, Room Coverage, Number of Mobs in Room, Encumberance etc.


        # List of Skills this character has in dictionary - SKILL - LEVEL

        self.db.skills = {'Hide': 3, 'Sneak': 1, 'Search': 2}

        #skill points to spend
        self.db.stat_skill_points = 3

        self.db.items_worn = []

    def get_attributes(self):
        """
        Simple access method to return MODIFIED attributes
        Returns list of Attributes

        This is the characters attributes with modifications from effects taken into account

        (agi, con, int, per, str)
        """

        return (rules.get_agility(self), rules.get_constitution(self), rules.get_intelligence(self), rules.get_perception(self), rules.get_strength(self))

    def get_skills(self):
        """
        Returns list of skills for view skills command
        """
        return self.db.skills
    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and
                   con.access(looker, "view"))
        things = []
        for con in visible:
            key = con.get_display_name(looker)
            if con.is_typeclass(Clothing, exact=True):
                clothingHelper = ClothingSlots()
                if clothingHelper.checkwearingit(self, con) == 1:
                    things.append("%s (%s)" % (key, con.db.worn_slot))
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            string += "%s" % desc
        if things:
            if self == looker:
                string += "\n|wYou are wearing:|n " + ", ".join(things)
            else:
                string += "\n|wThey are wearing:|n " + ", ".join(things)
        else:
            if self == looker:
                string += "\n|wYou are wearing your birthday suit.|n " + ", ".join(things)
            else:
                string += "\n|wThey are wearing... AVERT YOUR EYES!!!"

        return string


