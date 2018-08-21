
from objects import Object

#containers will be holster and bags etc. - something you store stuff in
#__containerslots__ = ['ankle', 'leftleg', 'rightleg', 'waistleft', 'waistright', 'chest', 'back', 'feet']
#weild be weapon slots - includes shields
#__wieldslots__ = ['hand1', 'hand2']


class Clothing(Object):
    """

    Clothing/Armour

    Clothing/Armour is interchangable in this Zombie Land
    It might not be your typical armour but has same effect.. heavy jacked is semi bite proof

    """

    def at_object_creation(self):
        super(Clothing, self).at_object_creation()
        # Zombie VS Physical - Denim would be VERY hard ot bite through, but a club would hurt, alot, or a knife
        self.db.defense_zombie = 0
        self.db.defense_physical = 0
        # bullets, arrows, bolts
        self.db.defense_penetration = 0

        # which armour slot can it be worn on
        # for simplicity one item per slot! and item come in pairs, i.e. gloves
        # Shields will take a weapons slot and a armour slot - checks required
        self.db.worn_slot = ''

        # is it a container and how big is it
        self.db.is_container = 0
        self.db.container_size = 0

        # is it a holster and what can it carry
        self.db.is_holster = 0
        self.db.holster_size = 0
        self.locks.add("equip:true()")

    def at_equip(self, character):
        # we'll call this in the "equip" command to modifier the characters defense
        # this would actually examine item for attribute modifiers and apply as required
        character.db.stat_defence_zombie += int(self.db.defense_zombie)

    def at_remove(self, character):
        character.db.stat_defence_zombie -= int(self.db.defense_zombie)
        if character.db.items_main_hand == self:
            character.db.items_main_hand = ''
        if character.db.items_off_hand == self:
            character.db.items_off_hand = ''

    def at_drop(self, dropper):
        #look like i need to override cmddrop and put this hook in there
        self.at_remove(dropper)


class Shield(Clothing):
    """

    Shield

    has similar properties to clothing/armour except worn on off-hand

    """

    def at_object_creation(self):
        super(Shield, self).at_object_creation()

    def at_equip(self, character):
        # call other at_equip - attach to offhand
        super(Shield, self).at_equip(character)
        character.db.items_off_hand = self

    def at_remove(self, character):
        # call other at_remove - attach to offhand
        super(Shield, self).at_remove(character)
        character.db.items_off_hand = None

    def at_drop(self, dropper):
        # call other at_drop - attach to offhand
        self.at_remove(dropper)


class ZWeapon(Object):
    """

    Weapons for killing Zombies or the living..

    At this stage it covers both Melee and Projectile
        Projectiles will have ammunition stored under weapon_projectile

    """

    def at_object_creation(self):
        super(ZWeapon, self).at_object_creation()
        # weapon Type - Melee or Projectile
        self.db.weapon_type = "Melee"

        # Object weapon requires to shoot
        # probably simplify guns to ignore clips
        self.db.weapon_projectile = ""

        # Number of shots between reloads
        # We can extend for bursts etc. later
        self.db.ammo_size = 1

        # damage dice
        self.db.damage = 1

        # Headshot Kill vs Zombie - Zombies have rotten heads, die easier, might vary on zombie type
        # Percentage modifier to single shot kill
        self.db.headshot_modifier = 20

        # Reload Time
        #   0 - shoot every round - bow (maybe)
        #   1 - one Round (cross bow)/Clip
        #   2 - 6 shooter?
        self.db.reload_time = 0

        # Hands required to wield
        self.db.one_handed = 1

    def at_equip(self, character):
        # we'll call this in the "equip" command to modifier the characters defense
        # this would actually examine item for attribute modifiers and apply as required
        character.db.items_main_hand = self

    def at_remove(self, character):
        character.db.items_main_hand = None
