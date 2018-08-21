
from evennia.commands.default.muxcommand import MuxCommand

from evennia.utils.evform import EvTable

from typeclasses.items import Clothing, ZWeapon, Shield
from world.rules_inventory import ClothingSlots
from world.rules_inventory import calculate_encumbrance_max, check_can_carry_item
from world.rules_inventory import calculate_encumbrance_now, check_container_size
from typeclasses.characters import Character


#Clothing will be armour - something you wear
#__clothingslots__ = ['feet', 'legs', 'torso', 'hands', 'arms', 'neck', 'head', 'face', 'back', 'chest']


class CmdInventory(MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """
    # Alternate version of the inventory command which separates
    # worn and carried items.

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """check inventory"""

        max_e = calculate_encumbrance_max(self.caller)
        now_e = calculate_encumbrance_now(self.caller)

        enc_string = "|GEncumbrance: %s/%s [%.0f%%]|n" % (now_e, max_e, (100 * now_e/max_e))

        if not self.caller.contents:
            self.caller.msg("You are not carrying or wearing anything.\n" + enc_string)
            return

        items = self.caller.contents
        if self.caller.db.items_main_hand is not None:
            items.remove(self.caller.db.items_main_hand)
        if self.caller.db.items_off_hand is not None:
            items.remove(self.caller.db.items_off_hand)


        carry_table = EvTable(border="header")
        wear_table = EvTable(border="header")
        for item in items:
            if item.is_typeclass(Clothing, exact=True):
                clothingHelper = ClothingSlots()
                if not clothingHelper.checkwearingit(self.caller, item) == 1:
                    carry_table.add_row("|C  %s|n" % item.name, item.db.desc or "")
                else:
                    wear_table.add_row("|C  %s (%s)|n" % (item.name, item.db.worn_slot), item.db.desc or "")
            else:
                carry_table.add_row("|C  %s|n" % item.name, item.db.desc or "")
        if carry_table.nrows == 0:
            carry_table.add_row("|CNothing.|n", "")
        string = "|wYou are carrying:\n%s" % carry_table

        if wear_table.nrows == 0:
            wear_table.add_row("|CNothing.|n", "")
        string += "|/|wYou are wearing:\n%s" % wear_table
        if self.caller.db.items_off_hand is not None or self.caller.db.items_main_hand is not None:
            string += "\n|wYou are holding:"
            if self.caller.db.items_main_hand is not None:
                string += "\n|C  %s (main hand) " % self.caller.db.items_main_hand.name
            if self.caller.db.items_off_hand is not None:
                string += "\n|C  %s (off hand) " % self.caller.db.items_off_hand.name

        string += "\n" + enc_string

        self.caller.msg(string)



class CmdGive(MuxCommand):
    """
    give away something to someone

    Usage:
      give <inventory obj> = <target>

    Gives an items from your inventory to another character,
    placing it in their inventory.
    """
    key = "give"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> = <target>")
            return
        to_give = caller.search(self.lhs, location=caller,
                                nofound_string="You aren't carrying %s." % self.lhs,
                                multimatch_string="You carry more than one %s:" % self.lhs)
        target = caller.search(self.rhs)

        if not (to_give and target):
            return
        if not target.is_typeclass(Character, exact=True):
            caller.msg("You can only give to another character.")
            return
        if target == caller:
            caller.msg("You keep %s to yourself." % to_give.key)
            return
        if not to_give.location == caller:
            caller.msg("You are not holding %s." % to_give.key)
            return

        if caller.db.items_off_hand is not None:
            caller.db.items_off_hand.at_remove(caller)
        if caller.db.items_main_hand is not None:
            caller.db.items_main_hand.at_remove(caller)

        clothinghelper = ClothingSlots()
        if clothinghelper.checkwearingit(caller, to_give) == 1:
            caller.db.items_worn.remove(to_give)
            caller.msg("|BYou remove {}.".format(to_give.name))

        # give object
        caller.msg("You give %s to %s." % (to_give.key, target.key))
        to_give.move_to(target, quiet=True)
        target.msg("%s gives you %s." % (caller.key, to_give.key))
        # Call the object script's at_give() method.
        to_give.at_give(caller, target)


class CmdPut(MuxCommand):
    """
    Put object into another object

    Usage:
      put <object> = <inventory_object>

    You can put something from either your inventory or the ground
    directly into a bag or similar.
    """
    key = "put"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: put <object> = <inventory_object>")
            return
        move_object = caller.search(self.lhs)
        to_object = caller.search(self.rhs, location=caller,
                                nofound_string="You aren't carrying %s." % self.rhs,
                                multimatch_string="You carry more than one %s:" % self.rhs)

        if not (move_object and to_object):
            return

        if not (move_object.location == caller or move_object.location == caller.location):
            caller.msg("The %s isn't on the ground or in your inventory." % move_object.key)
            return

        if not to_object.db.is_container == 1:
            caller.msg("You can not put items in %s." % to_object.name)
            return

        if not check_container_size(to_object, move_object):
            caller.msg("It doesn't quite fit in the %s; need a large container?" % to_object.name)
            return

        # if worn - remove the item being worn
        clothinghelper = ClothingSlots()
        if clothinghelper.checkwearingit(caller, move_object) == 1:
            caller.db.items_worn.remove(move_object)
            caller.msg("|BYou remove {}.".format(move_object.name))

        if move_object.location == caller:
            allmsg = '%s scrummages in their %s' % (caller.name, to_object.name)
        else:
            if check_can_carry_item(caller, move_object):
                allmsg = '%s picks up %s and puts it in their %s' % (caller.name, move_object.key, to_object.name)
            else:
                caller.msg("Picking up the %s would over encumber you." % to_object.name)
                return

        move_object.move_to(to_object, quiet=True)
        caller.msg("You put %s in %s." % (move_object.key, to_object.key))
        caller.location.msg_contents(allmsg,
                                     exclude=caller)
        calculate_encumbrance_now(caller)

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

        if caller.db.items_off_hand is not None:
            if caller.db.items_off_hand.is_typeclass(ZWeapon, exact=True):
                caller.db.items_off_hand.at_remove(caller)
        if caller.db.items_main_hand is not None:
            if caller.db.items_main_hand.is_typeclass(ZWeapon, exact=True):
                caller.db.items_main_hand.at_remove(caller)
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
        elif obj.is_typeclass(Shield, exact=True):
            if caller.db.items_main_hand and caller.db.items_main_hand.db.one_handed == 0:
                caller.msg("You can not wield the %s as you have a two-handed weapon." % obj.name)
                return
            if caller.db.items_off_hand is not None:
                caller.msg("|BYou remove the %s first." % caller.db.items_off_hand.name)
            caller.msg("You equip the %s on your off hand." % obj.name)
            caller.location.msg_contents(("%s equips their %s." %
                                          (caller.name, obj.name)), exclude=caller)
            obj.at_equip(caller)
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
                    caller.location.msg_contents("%s is now wearing %s." %
                                                 (caller.name,
                                                  obj.name),
                                                 exclude=caller)
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
        foundobj = None
        if not obj:
            return
        else:
            if self.caller.db.items_main_hand == obj:
                foundobj = obj
            elif self.caller.db.items_off_hand == obj:
                foundobj = obj
            else:
                clothingHelper = ClothingSlots()
                if clothingHelper.checkwearingit(caller, obj) == 1:
                    foundobj = obj
                    caller.db.items_worn.remove(obj)

            if foundobj is not None:
                caller.msg("|BYou remove {}.".format(foundobj.name))
                caller.location.msg_contents("{} removes {}.".format(caller.name, foundobj.name), exclude=caller)
                foundobj.at_remove(caller)
            else:
                caller.msg("You don't seem to be wearing {}.".format(obj.name))




class CmdEmpty(MuxCommand):
    """
    Empty an Item

    Usage:
      empty <item>
      empty <item> = room
      empty <item> = <inventoryitem>

    Empties an item either to your inventory or into another item

    Defaults to emptying the item into your inventory.
    room will empty it to the floor in the room
    inventoryitem will poor the items into another item if it has room
    """
    key = "empty"
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("empty what?")
            return

        obj = caller.search(
            self.lhs,
            candidates=caller.contents,
            nofound_string="You do not have {}".format(args))

        isContainer = 0

        if not obj:
            return
        else:
            if not obj.contents:
                caller.msg("The %s appears to be empty." % obj.name)
            else:
                items = obj.contents

                if self.rhs:
                    if self.rhs == "room":
                        emptylocation = self.caller.location
                        msg = "%s empties the %s to the floor." % (caller.name, obj.name)
                        msgyou = "You empty the %s to the floor." % obj.name
                    else:
                        rec = caller.search(
                            self.rhs,
                            candidates=caller.contents,
                            nofound_string="Can not find the {}".format(args))
                        if not rec:
                            return
                        emptylocation = rec
                        isContainer = 1
                        if not rec.db.is_container == 1:
                            caller.msg("You can not put items in %s." % rec.name)
                            return
                        msg = "%s reshuffles his equipment." % caller.name
                        msgyou = "You empty %s into %s." % (obj.name, rec.name)
                else:
                    emptylocation = self.caller
                    msg = "%s reshuffles his equipment." % caller.name
                    msgyou = "You empty %s into your inventory." % obj.name

                for item in items:
                    if isContainer == 1:
                        if not check_container_size(emptylocation, item):
                            caller.msg("%s did not fit in %s." % (item.name, emptylocation.name))
                        else:
                            item.move_to(emptylocation, quiet=True)
                    else:
                        item.move_to(emptylocation, quiet=True)
                caller.msg(msgyou)
                caller.location.msg_contents(msg, exclude=caller)
                calculate_encumbrance_now(caller)


class CmdWield(MuxCommand):
    """
    Wield an item as a weapon

    Usage:
      wield <item>

    Uses the item as a weapon

    """
    key = "weild"
    aliases = ["wield"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Wield what?")
            return

        obj = caller.search(
            args,
            candidates=caller.contents,
            nofound_string="You do not have {}".format(args))

        if not obj:
            return

        elif obj.is_typeclass(ZWeapon, exact=True):

            if obj.db.weapon_type not in caller.db.skills:
                caller.msg("You don't have the skills wield the %s." % obj.name)
                return
            if caller.db.items_off_hand and obj.db.one_handed == 0:
                caller.msg("Looks like you have your hands full; unequip the %s first." % caller.db.items_off_hand.name)
                return
            if caller.db.items_main_hand:
                caller.msg("|BYou remove the %s first." % caller.db.items_main_hand.name)

            caller.msg("You wield the %s and it feels goooood." % obj.name)
            caller.location.msg_contents(("%s wields their %s and appears happy with the result." %
                                          (caller.name, obj.name)) , exclude=caller)

            obj.at_equip(caller)
        else:
            caller.msg("You can't wield {}.".format(
                obj.get_display_name(caller)))
