

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

