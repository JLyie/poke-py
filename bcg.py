'''
This module is made for CardPy versions 2.3 and above. It is a battle card game (BCG) where you use
battle cards that you collect/trade and fight until you win. Work In Progress -May 11, 2026 PhST-
'''

CARD_STATS = {  # TODO #1: Finalize creature attributes and substitute placeholders.
    "Pykagloo": {"hp": ..., "atk": ..., "def": ...},
    "Fireguard": {"hp": ..., "atk": ..., "def": ...},
    "Spookie": {"hp": ..., "atk": ..., "def": ...},
    "Bloomey": {"hp": ..., "atk": ..., "def": ...}
}


def get_card_stats(card):
    creature = card['name'].split(' ', 1)[1]  # "Rare Pikagloo" → "Pikagloo"
    stats = CARD_STATS.get(creature)
    return stats


def load_player_collection():
    filepath = "Database/carddata.json"


def player_pick_card(): ...


def npc_pick_card(collection): ...


def calculate_damage(player_dmg, player_hp, npc_dmg, npc_hp): ...


def start_battle(): ...
