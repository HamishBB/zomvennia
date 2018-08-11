"""
Rules

Start of the rules files - Keep formulas etc in one location for easy updating

This may need to be broken up into logical components later

i.e. rules_combat/rules_skills/

"""


def get_agility(character):
    """
    Used to calculate the current agility stat of character.
    Characters will have their base
        character.db.attr_agility
    However this will be effected by encumbrance (and other?) factors

    :return:
    """
    if (character.db.stat_encumbrance_max == 0):
        encumbered = 0
    else:
        encumbered = character.db.stat_encumbrance_now / float(character.db.stat_encumbrance_max)
    stat = character.db.attr_agility

    # If more than 50% encumbrance, knock off 20% stealth
    # just made this up.. totally not thought out
    if encumbered > 0.5:
        stat = stat * 0.8
    
    return int(stat)


def get_perception(character):
    """
    Used to calculate the current perception stat of character.
    Characters will have their base
        character.db.attr_perception
    However being tired will modify this - more to come

    :return:
    """
    if (character.db.stat_energy == 0):
        energy_ratio = 0
    else:
        energy_ratio = character.db.stat_energy_current / float(character.db.stat_energy)

    stat = character.db.attr_perception

    # Just as a demo of what could effect it
    if energy_ratio < 0.8:
        stat = stat * energy_ratio

    return int(stat)



def get_strength(character):
    """
    Used to calculate the current stealth stat of character.
    Characters will have their base
        character.db.attr_strength

    This will apply any modifiers here

    :return:
    """

    stat = character.db.attr_strength

    return int(stat)

def get_intelligence(character):
    """
    Used to calculate the current stealth stat of character.
    Characters will have their base
        character.db.attr_intelligence

    This will apply any modifiers here

    :return:
    """

    stat = character.db.attr_intelligence

    return int(stat)

def get_constitution(character):
    """
    Used to calculate the current stealth stat of character.
    Characters will have their base
        character.db.attr_constitution

    This will apply any modifiers here

    :return:
    """

    stat = character.db.attr_constitution

    return int(stat)