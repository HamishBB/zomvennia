
from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.items import Clothing
from world.rules_inventory import ClothingSlots

#Clothing will be armour - something you wear
#__clothingslots__ = ['feet', 'legs', 'torso', 'hands', 'arms', 'neck', 'head', 'face', 'back', 'chest']

class CmdDrop(MuxCommand):
    """
    drop something

    Usage:
      drop <obj>

    Lets you drop an object from your inventory into the
    location you are currently in.
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    help_category = "Items"

    def func(self):
        """Implement command"""

        caller = self.caller
        if not self.args:
            caller.msg("You drop the only thing that smells worse than the zombies!")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        obj = caller.search(self.args, location=caller,
                            nofound_string="You aren't carrying %s." % self.args,
                            multimatch_string="You carry more than one %s:" % self.args)
        if not obj:
            return
        clothingHelper = ClothingSlots()
        if clothingHelper.checkwearingit(caller, obj) == 1:
            caller.db.items_worn.remove(obj)
            caller.msg("|BYou remove {}.".format(obj.name))
            # super(Clothing, self).at_drop(dropper)
        obj.move_to(caller.location, quiet=True)
        caller.msg("You drop %s." % (obj.name,))
        caller.location.msg_contents("%s drops %s." %
                                     (caller.name, obj.name),
                                     exclude=caller)
        # Call the object script's at_drop() method.
        obj.at_drop(caller)

class CmdWear(MuxCommand):
    """
    wear an item

    Usage:
      wear <item>

    Equips a article of clothing or armour onto your character
    
    Everyone should look good dying...
    """
    key = "wear"
    aliases = ["equip"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Wear what?")
            return

        obj = caller.search(
            args,
            candidates=caller.contents,
            nofound_string="You do not have {}".format(args))

        if not obj:
            return

        elif obj.is_typeclass(Clothing, exact=True):
            if obj.db.worn_slot == '':
                caller.msg("It looks like clothing but where do we put it??")
                return
            clothingHelper = ClothingSlots()
            if clothingHelper.checkwearingit(caller, obj) == 1:
                caller.msg("You're already wearing the {}.".format(obj))
                return
            if obj.db.worn_slot in clothingHelper.clothingslots:
                spot_filled = clothingHelper.checkslotfree(caller,obj)
                if spot_filled == 1:
                    caller.msg("You can't wear two items on your {}.".format(obj.db.worn_slot))
                else:
                    caller.db.items_worn.append(obj)
                    caller.msg("|BYou are now wearing {}.".format(obj.name))
                    obj.at_equip(caller)
            else:
                caller.msg("You look for your {} but it must have fallen off.".format(obj.db.worn_slot))

        else:
            caller.msg("You can't wear {}.".format(
                obj.get_display_name(caller)))


class CmdRemove(MuxCommand):
    """
    Remove an item

    Usage:
      remove <item>

    Removes a article of clothing or armour onto your character

    Some parties are best attended nakid.
    """
    key = "remove"
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("remove what?")
            return

        obj = caller.search(
            args,
            candidates=caller.contents,
            nofound_string="You do not have {}".format(args))

        if not obj:
            return

        else:
            clothingHelper = ClothingSlots()
            if clothingHelper.checkwearingit(caller, obj) == 1:
                caller.db.items_worn.remove(obj)
                caller.msg("|BYou remove {}.".format(obj.name))
                obj.at_remove(caller)
            else:
                caller.msg("You don't seem to be wearing {}.".format(obj.name))