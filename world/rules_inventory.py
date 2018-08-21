def calculate_encumbrance_max(character):
    """
    Used to calculate the characters max encumbrance

    For every strength they can carry 5kgs MAX

    """

    encumbrance = character.db.attr_strength * 5000
    character.db.stat_encumbrance_max = encumbrance

    return int(encumbrance)


def calculate_encumbrance_now(character):
    """
    Used to calculate the characters max encumbrance

    For every strength they can carry 5kgs MAX

    """
    items = character.contents
    encumbrance = 0
    for item in items:
        encumbrance += int(item.db.weight)
        if len(item.contents) > 0:
            more_items = item.contents
            for more_item in more_items:
                encumbrance += int(more_item.db.weight)

    character.db.stat_encumbrance_now = encumbrance
    return int(encumbrance)


def check_can_carry_item(character, item_receiving):
    """

    Used to confirm the character will not be over encumbered
    when about to receive an object

    """

    encumbrance_now = calculate_encumbrance_now(character)
    encumbrance_max = calculate_encumbrance_max(character)
    if (encumbrance_now + item_receiving.db.weight) > encumbrance_max:
        return 0
    else:
        return 1


def check_container_size(item_receiving, item_received):
    """

    Used to confirm the object (item_received) will fit into
    the object about receiving (item_receiving)

    """
    if not item_receiving.db.is_container == 1:
        return 0

    items = item_receiving.contents
    total = 0
    for item in items:
        total += item.db.size

    total += item_received.db.size

    if total > item_receiving.db.container_size:
        return 0
    else:
        return 1

class ClothingSlots():
    """
    Helper Class to store the slot info

    Currently really simple, you can wear one item in each spot
    """

    clothingslots = ['feet', 'legs', 'torso', 'hands', 'arms', 'neck', 'head', 'face', 'back', 'chest']

    def checkslotfree(self, character, item):
        spot_filled = 0
        for wi in character.db.items_worn:
            if item.db.worn_slot == wi.db.worn_slot:
                spot_filled = 1
        return spot_filled

    def checkwearingit(self, character, item):
        if item in character.db.items_worn:
            return 1
        else:
            return 0

