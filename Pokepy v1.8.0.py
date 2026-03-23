'''
A card game project by devJL.

Created on March ?, 2026. This is an updated version that releases on March 31, 2026.
This version (1.8.0) is NOT YET released. Current Released Version: Pokepy v1.6.4

Pokepy v(1.8.0)
'''

import sys
import os
import time
import random
import colorama
from colorama import Fore, init, Back
from datetime import datetime
import json


class Card:
    def __init__(self, name, rarity, border, image_quality, worth):
        self.name = name
        self.rarity = rarity
        self.border = border
        self.image_quality = image_quality
        self.worth = worth

    def __str__(self):
        return f"{self.name} ({self.rarity}) - ${self.worth}"

    def to_dict(self):
        return {
            "name": self.name,
            "rarity": self.rarity,
            "border": self.border,
            "image_quality": self.image_quality,
            "worth": self.worth
        }


class Pack:
    def __init__(self):
        self.cards = []
        self.prob = {
            "Common": 0.6,
            "Uncommon": 0.25,
            "Rare": 0.1,
            "legendary": 0.05
        }
        self.borders = ["Holo", "Non-Holo", "Foil"]
        self.image_qualities = ["Good", "Excellent", "Mint"]

    def generate_card(self):
        rarity = random.choices(list(self.prob.keys()),
                                weights=self.prob.values())[0]
        border = random.choice(self.borders)
        image_quality = random.choice(self.image_qualities)
        worth = self.calculate_worth(rarity, border, image_quality)
        name = f"{rarity} {random.choice(['Pikachu', 'Charizard', 'Bulbasaur', 'Squirtle', 'Eevee'])}"
        return Card(name, rarity, border, image_quality, worth)

    def calculate_worth(self, rarity, border, image_quality):
        worth = 0
        if rarity == "Common":
            worth = 1
        elif rarity == "Uncommon":
            worth = 5
        elif rarity == "Rare":
            worth = 20
        elif rarity == "Legendary":
            worth = 100
        if border == "Holo":
            worth *= 1.5
        elif border == "Foil":
            worth *= 2
        if image_quality == "Excellent":
            worth *= 1.2
        elif image_quality == "Mint":
            worth *= 1.5
        return round(worth, 2)

    def open_pack(self):
        pack_value = 0
        cards = []
        for _ in range(5):
            card = self.generate_card()
            cards.append(card)
            pack_value += card.worth
        return cards, pack_value


class ClassIcard:
    def __init__(self, Icard):
        self.Icard = Icard

    def __str__(self):
        return self.Icard

    def to_dict(self, quantity=1):
        return {
            "item_name": self.Icard,
            "quantity": quantity
        }


class ItemPack:
    def __init__(self):
        self.items = ["Astral Wand", "Fiery Leather",
                      "Quantum Ball", "Celestial Wand", "Orbital Boots"]

    def generate_Icard(self):
        item = random.choices(list(self.items))[0]
        return ClassIcard(item)

    def open_Ipack(self):
        cards = []
        for _ in range(5):
            card = self.generate_Icard()
            cards.append(card)
        return cards


class Player:
    def __init__(self):
        self.collection = []
        self.collectiondict = {}
        self.items = []
        self.coins = []
        self.level = 1
        self.exp = 0

    def add_cards(self, cards):
        os.makedirs("Database", exist_ok=True)
        filepath = "Database/carddata.json"

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        for card in cards:
            existing_data.append(card.to_dict())

        with open(filepath, "w") as f:
            json.dump(existing_data, f, indent=4)

    def auto_addItems(self, item_counts):
        os.makedirs("Database", exist_ok=True)
        filepath = "Database/itemdata.json"

        # Initialize first to avoid UnboundLocalError
        existing_data = []

        # Then try to read existing data
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
                if content.strip():
                    existing_data = json.loads(content)

        # Modify
        for name, qty in item_counts.items():
            for existing_item in existing_data:
                if existing_item["item_name"] == name:
                    existing_item["quantity"] += qty
                    break
            else:
                existing_data.append(ClassIcard([name]).to_dict(qty))

        # Write
        with open(filepath, "w") as f:
            json.dump(existing_data, f, indent=4)

    def view_collection(self):
        print("Your Card Collection:")
        for i, card in enumerate(self.collection):
            print(f"{i+1}. {card}")

    def view_items(self):
        print("Your item inventory:")
        for i, item in enumerate(self.items):
            print(f"{i+1}. {item}")

    # UPDATED fixed gain_exp *upd-007.cd-220326
    def gain_exp(self, amount):
        if self.level >= 50:
            print(f"{Fore.RED}You're at max level!{Fore.RESET}")
            return
        self.exp += amount
        print(f"{Fore.GREEN}You gained {amount} EXP!{Fore.RESET}")
        self.check_level_up()
        self.save_progress()

    # UPDATED new check_level_up *upd-006.cd-220326
    def check_level_up(self):
        while self.level < 50:
            level_up_exp = int(100 * (self.level ** 1.5))
            if self.exp >= level_up_exp:
                self.exp -= level_up_exp
                self.level += 1
                print(
                    f"{Fore.GREEN}You just leveled up to Level {self.level}!{Fore.RESET}")
            else:
                break

    # UPDATED new save_progress *upd-008.cd-220326
    def save_progress(self):
        os.makedirs("Database", exist_ok=True)
        filepath = "Database/expdata.json"
        data = {
            "level": 1,
            "exp": 0
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    # UPDATE: new load_progress *upd-005.cd-220326
    def load_progress(self):
        os.makedirs("Database", exist_ok=True)
        filepath = "Database/expdata.json"

        if not os.path.exists(filepath):
            default_data = {"level": 1, "exp": 0}
            with open(filepath, "w") as f:
                json.dump(filepath, f, indent=4)
            return

        with open(filepath, "r") as f:
            content = f.read()
            if content.strip():
                data = json.loads(content)
                self.level = data.get("level", 1)
                self.exp = data.get("exp", 0)

    # UPDATED add_coins now functioning *upd-003.cd-220326
    def add_coins(self, amount):
        os.makedirs("Database", exist_ok=True)
        FILEPATH = "Database/coinsdata.json"

        existing_data = {"coins": 0}

        if os.path.exists(FILEPATH):
            with open(FILEPATH, "r") as f:
                content = f.read()
                if content.strip():
                    existing_data = json.loads(content)

        existing_data["coins"] += amount

        with open(FILEPATH, "w") as f:
            json.dump(existing_data, f, indent=4)

        print(
            f"{Fore.YELLOW}+{amount} coins added! Total: {existing_data['coins']} coins.{Fore.RESET}")

    # UPDATED: spend_money now functioning *upd-004.cd-220326
    def spend_money(self, amount):
        filepath = "Database/coinsdata.json"

        # Read current coins
        existing_data = {"coins": 0}
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
                if content.strip():
                    existing_data = json.loads(content)

        # Check if enough coins
        if amount > existing_data["coins"]:
            print(
                f"{Fore.RED}Not enough coins! You have {existing_data['coins']} coins.{Fore.RESET}")
            return False

        # Deduct coins
        existing_data["coins"] -= amount

        # Save to JSON
        with open(filepath, "w") as f:
            json.dump(existing_data, f, indent=4)

        print(
            f"{Fore.YELLOW}-{amount} coins spent! Remaining: {existing_data['coins']} coins.{Fore.RESET}")
        return True

    def show_stats(self):
        os.makedirs("Database", exist_ok=True)
        FILEPATH1 = "Database/coinsdata.json"
        coins = 0  # default if file doesn't exist yet
        if os.path.exists(FILEPATH1):
            with open(FILEPATH1, "r") as f:
                content = f.read()
                if content.strip():
                    coins = json.loads(content)["coins"]

        next_level_exp = int(100 * (self.level ** 1.5)
                             ) if self.level < 50 else 0

        print("\n=== PLAYER STATS ===")
        print(f"Level    : {self.level}{' (MAX)' if self.level == 50 else ''}")
        print(
            f"EXP      : {self.exp} / {next_level_exp if self.level < 50 else 'MAX'}")
        print(f"Coins    : {coins}")
        print("====================\n")

    def startup(self):
        global startup
        startup = datetime.now().strftime("%H:%M:%S")
        print(f"Your startup time is: {startup}")
        time.sleep(1)
        pass


class Trade:
    def __init__(self):
        global active_bots, total_bots, trade_items
        total_bots = 10
        active_bots = random.randint(1, 10)
        trade_items = ["Astral Wand", "Upgrade Card",
                       "Chest", "Celestial Wand"]

   # global randbots

    # def randbots(self):
        #   if inactive_bots < 0:
      #      absol = abs(inactive_bots)
       #     print(f"Changed to absol. {absol}")
        #    inactive_bots = absol
        #   time.sleep(10)
        #  return active_bots, inactive_bots

    def verify(self, trade_arg, inv):
        print

    def cts(self):
        inactive_bots = abs(10 - active_bots)
        print("TRADING BOTS:\n"
              f"Active Bots: {active_bots}\n"
              f"Sleeping Bots: {inactive_bots}\n"
              )
        if active_bots and inactive_bots == 0:
            print("\nAll trading bots are currently asleep. Come back later!")
            time.sleep(2)
            main()
        else:
            pass
        randitem = random.choice(trade_items)
        randq = 5
        stocklist = ["ON STOCK", "NO STOCK"]
        randchoice = random.choice(stocklist)
        print("Welcome to the Trading Hub, player!\n")
        print("CURRENT TRADE INVENTORY\n"
              f"1. Astral Wand for {randq} Magical Powder\n"
              f"2. Upgrade Card for {randq} Quantum Ball\n"
              f"3. Chest for {randq + 5} Magical Powder\n"
              f"4. Celestial Wand - {randchoice}\n"
              )
        if randchoice == "ON STOCK":
            print(
                f"Celestial Wand for 3 Fiery Leather, 5 Magical Powder, 1 Celestial Wand, and 1 Quantum Ball ")
        else:
            pass
        inp = input("Please select an item to trade: ")
        if inp == "1":
            print
        elif inp == "2":
            print
        elif inp == "3":
            print
        elif inp == "4":
            print
        else:
            print("Item entered is either not on stock or not found.")
            time.sleep(3)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# MAIN

def main():
    pack = Pack()
    p = Player()
    Ipack = ItemPack()
    trade = Trade()
    p.startup()
    while True:
        clear_screen()
        print("Hello! Welcome to Pokepy by PyDevelopments! Version 1.8.0\n")
        print("NOTE: This update only partially saves your game data. A few more patches! \n", file=sys.stderr)
        time.sleep(2)
        print(
            "1. Open a pack\n"
            "2. Player Stats\n"
            "3. View Inventory/Collection\n"
            "4. Daily Reward(INACTIVE)\n"
            # EDITED: New header. Func CUS *upd-009.cd-230326
            "5. Modify Cards (INACTIVE)\n"
            "6. Special Events (INACTIVE)\n"
            "7. Shop (INACTIVE)\n"
            "8. Exit\n"
        )
        x = input("Choose an option: ")
        if x == '1':
            print(
                "1. Card Pack\n"
                "2. Item Pack\n"
            )
            c = input("Choose a pack: ")
            if c == '1':
                cards, pack_value = pack.open_pack()
                print("Nice! You opened a pack. Here's what you got:")
                time.sleep(2)
                for i, card in enumerate(cards):
                    print(f"{i+1}. {card}")
                print(f"Total pack value: ${pack_value}")
                time.sleep(2)
                p.add_cards(cards)
                time.sleep(1)
                p.gain_exp(100)
                print()  # Blank Line
                input("Press ENTER to continue...")
            elif c == '2':
                item = Ipack.open_Ipack()
                print("Nice! Here are the items you got:")
                time.sleep(1.5)
            for x, items in enumerate(item):
                # EDITED: Removed [0] *upd-001.cd-220326
                print(f"{x+1}. {items.Icard}")
                item_counts = {}
                for card in item:
                    name = card.Icard  # EDITED: Removed [0] *upd-002.cd-220326
                    item_counts[name] = item_counts.get(name, 0) + 1
            print("You may use these items to upgrade your Pokemon © cards.")
            p.auto_addItems(item_counts)
            input("Press ENTER to continue playing...")
        elif x == "2":
            p.show_stats()
            input("Press ENTER to continue...")
        elif x == "3":
            print(
                "1. View Card Collection\n"
                "2. View Item Inventory\n"
            )
            opt = input("Please pick an option: ")
            if opt == '1':
                p.view_collection()
                input("Press ENTER to continue playing...")
            elif opt == '2':
                p.view_items()
                input("Press ENTER to continue playing...")
            else:
                pass
        elif x == "4":
            print("Updating..")
        elif x == "5":
            print("UPDATING")  # CUS
            input("Press ENTER to continue playing...")
        elif x == "6":
            print("Still working on this one!")
            time.sleep(2)
            main()
        elif x == "7":
            trade.cts()
        elif x == "8":
            print("Thank you for playing! See you again!")
            time.sleep(2)
            sys.exit()


if __name__ == '__main__':
    main()
