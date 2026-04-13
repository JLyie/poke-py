

import matplotlib.pyplot as plt
import sys
import os
import time
import random
import colorama
from colorama import Fore, init, Back
from datetime import datetime, timedelta
import json
import traceback
import pygame
import matplotlib
matplotlib.use('Agg')  # use non-interactive backend


if getattr(sys, 'frozen', False):
    # Running as exe
    os.chdir(os.path.dirname(sys.executable))
else:
    # Running as .py in VS Code
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
RARITY_TIERS = ["Common", "Uncommon", "Rare", "Legendary"]
# "Rainbow" Quality can only be obtained from NPC Trades
BORDER_TIERS = ["Non-Holo", "Foil", "Holo", "Rainbow"]
# "Perfect" Quality can only be obtained from NPC Trades
QUALITY_TIERS = ["Poor", "Good", "Excellent", "Perfect"]

RARITY_WORTH = {"Common": 1, "Uncommon": 3, "Rare": 20, "Legendary": 100}
BORDER_WORTH = {"Non-Holo": 1.5, "Foil": 2, "Holo": 3.5, "Rainbow": 8}
# "Perfect" Quality can only be obtained from NPC Trades
QUALITY_WORTH = {"Poor": 0.5, "Good": 1, "Excellent": 2.6, "Perfect": 4}

UPGRADE_COSTS = {
    1: {"items": {"Upgrade Card": 1, "Magical Powder": 2}, "coins": 10},
    2: {"items": {"Upgrade Card": 1, "Fiery Leather": 2}, "coins": 25},
    3: {"items": {"Upgrade Card": 2, "Void Crystal": 1, "Quantum Ball": 2}, "coins": 100}
}

SPECIAL_EVENTS = [
    {
        "name": "Coin Frenzy",
        "type": "bonus_coins",
        "description": "All coin rewards are doubled!",
        "multiplier": 2
    },
    {
        "name": "Rare Drop Festival",
        "type": "rare_items",
        "description": "Rare items drop more frequently from chests!",
        "bonus_items": {"Void Crystal": 1, "Upgrade Card": 1}
    },
    {
        "name": "Flash Sale",
        "type": "limited_shop",
        "description": "Special limited items available in the shop!",
        "limited_items": {
            "Mystery Box": {"cost": {"Magical Powder": 3}, "reward": {"Void Crystal": 1, "Celestial Wand": 1}},
            "Booster Bundle": {"cost": {"Fiery Leather": 2}, "reward": {"Quantum Ball": 3, "Magical Powder": 5}}
        }
    }
]

EVENT_DURATIONS = {
    "short": 1/24,    # 1 hour in days
    "medium": 1,      # 24 hours
    "long": 3         # 3 days
}


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
            "Legendary": 0.05
        }
        self.borders = ["Holo", "Non-Holo", "Foil"]
        self.image_qualities = ["Good", "Excellent", "Mint"]

    def generate_card(self):
        rarity = random.choices(list(self.prob.keys()),
                                weights=self.prob.values())[0]
        border = random.choice(self.borders)
        image_quality = random.choice(self.image_qualities)
        worth = self.calculate_worth(rarity, border, image_quality)
        # Changed names
        name = f"{rarity} {random.choice(['Pikagloo', 'Fireguard', 'Balbuzer', 'Spookie', 'Bloomey'])}"
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
            worth *= 2
        elif border == "Foil":
            worth *= 1.5
        elif border == "Non-Holo":
            worth *= 1
        if image_quality == "Excellent":
            worth *= 1.5
        elif image_quality == "Good":
            worth *= 1.2
        elif image_quality == "Mint":
            worth *= 1.7
        return round(worth, 2)

    def open_pack(self):
        pack_value = 0
        cards = []
        for _ in range(5):
            card = self.generate_card()
            cards.append(card)
            pack_value += card.worth
        return cards, pack_value

    def verify(self):
        open_filepath = "Database/openpackdata.json"
        exp_filepath = "Database/expdata.json"
        exp_data = {"level": 1, "exp": 0}
        os.makedirs("Database", exist_ok=True)

        if os.path.exists(exp_filepath):
            with open(exp_filepath, "r") as a:
                content_exp = a.read()
                if content_exp.strip():
                    exp_data = json.loads(content_exp)

        level_req = exp_data["level"] >= 10  # ✅ clean one liner

        today = datetime.now().strftime("%Y-%m-%d")
        open_data = {"date": today, "opens_left": 10}

        if os.path.exists(open_filepath):
            with open(open_filepath, "r") as b:
                content = b.read()
                if content.strip():
                    open_data = json.loads(content)
                    if open_data["date"] != today and level_req:
                        open_data = {"date": today, "opens_left": 10}

        if not level_req:
            time.sleep(2)
            return True  # ✅ under level 10, unlimited opens

        if open_data["opens_left"] <= 0:
            print(
                f"{Fore.RED}You've reached your daily pack open limit! Come back tomorrow.{Fore.RESET}")
            return False

        # Deduct one open and save
        open_data["opens_left"] -= 1
        with open(open_filepath, "w") as c:
            json.dump(open_data, c, indent=4)

        print(
            f"{Fore.YELLOW}Pack opens remaining today: {open_data['opens_left']}/10{Fore.RESET}")
        return True


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
                      "Quantum Ball", "Orbital Boots", "Magical Powder"]

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
                existing_data.append(ClassIcard(name).to_dict(qty))

        # Write
        with open(filepath, "w") as f:
            json.dump(existing_data, f, indent=4)

    def view_collection(self):
        filepath = "Database/carddata.json"

        if not os.path.exists(filepath):
            print("No card collection found.")
            return

        with open(filepath, "r") as f:
            content = f.read()
            if not content.strip():
                print("Your card collection is empty.")
                return
            cards = json.loads(content)

        print("\n=== YOUR CARD COLLECTION ===")
        for i, card in enumerate(cards, start=1):
            print(f"{i}. {card['name']}")
            print(f"   Rarity       : {card['rarity']}")
            print(f"   Border       : {card['border']}")
            print(f"   Image Quality: {card['image_quality']}")
            print(f"   Worth        : ${card['worth']:.2f}")
            print()
        print(f"Total cards: {len(cards)}")
        print("============================\n")

    def view_items(self):
        filepath = "Database/itemdata.json"

        if not os.path.exists(filepath):
            print("No item inventory found.")
            return

        with open(filepath, "r") as f:
            content = f.read()
            if not content.strip():
                print("Your item inventory is empty.")
                return
            items = json.loads(content)

        print("\n=== YOUR ITEM INVENTORY ===")
        for i, item in enumerate(items, start=1):
            print(f"{i}. {item['item_name']} x{item['quantity']}")
        print("===========================\n")

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
    def check_level_up(self, sound_manager=None):
        while self.level < 50:
            level_up_exp = int(100 * (self.level ** 1.5))
            if self.exp >= level_up_exp:
                self.exp -= level_up_exp
                self.level += 1
                print(
                    f"{Fore.GREEN}You just leveled up to Level {self.level}!{Fore.RESET}")
                if sound_manager:
                    sound_manager.play_sfx("level_up.mp3")
            else:
                break

    # UPDATED new save_progress *upd-008.cd-220326
    def save_progress(self):
        os.makedirs("Database", exist_ok=True)
        filepath = "Database/expdata.json"
        data = {
            "level": self.level,
            "exp": self.exp
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
                json.dump(default_data, f, indent=4)
            return

        with open(filepath, "r") as f:
            content = f.read()
            if content.strip():
                data = json.loads(content)
                self.level = data.get("level", 1)
                self.exp = data.get("exp", 0)

    # UPDATED add_coins now functioning *upd-003.cd-220326
    def add_coins(self, amount, event=None):
        if event:
            from __main__ import SpecialEvents
            amount = SpecialEvents().apply_bonus_coins(amount, event)
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

    def upgrade_card(self, p_coins):
        filepath = "Database/carddata.json"
        exp_filepath = "Database/expdata.json"
        level_req = False
        upd_type = 0  # 0 = Basic | 1 = Advanced

        if not os.path.exists(filepath):
            print("No card collection found.")
            return

        with open(filepath, "r") as f:
            content = f.read()
            if not content.strip():
                print("Your card collection is empty.")
                return
            cards = json.loads(content)

        with open(exp_filepath, "r") as e:
            exp_content = e.read()
            exp = json.loads(exp_content)["level"]

        if exp >= 10:
            level_req = True

        print("=== SELECT UPGRADE TYPE ===\n"
              "1. Basic Upgrade\n"
              "2. Advanced Upgrade\n"
              )

        inp = input("Select an Upgrade Type: ").strip()

        if inp not in ("1", "2"):
            print(
                "Please enter a valid number and don't leave the space blank. Try again.")
            time.sleep(2)
            return

        if inp == "2" and level_req:
            upd_type = 1
            print("Currently in Advanced mode.\n")
            time.sleep(2)
        elif inp == "2" and level_req is False:
            print(
                f"You are currently not eligible for this Upgrade Type. Your current level is {exp}. Only Lvl 10 and above are allowed.\n")
            input("Press ENTER to continue...")
            return
        elif inp == "1":
            print("Currently in Basic mode\n")
            time.sleep(2)

        # Show collection
        print("\n=== SELECT A CARD TO UPGRADE ===")
        for i, card in enumerate(cards, start=1):
            print(
                f"{i}. {card['name']} | Rarity: {card['rarity']} | Border: {card['border']} | Quality: {card['image_quality']} | Worth: ${card['worth']:.2f}")
        print()

        # Select card
        try:
            choice = int(input("Select a card number (0 to cancel): "))
            if choice == 0:
                return
            if choice < 1 or choice > len(cards):
                print("Invalid choice.")
                return
        except ValueError:
            print("Please enter a valid number.")
            return

        selected_card = cards[choice - 1]
        print(f"\nSelected: {selected_card['name']}")
        print(
            f"Rarity: {selected_card['rarity']} | Border: {selected_card['border']} | Quality: {selected_card['image_quality']}")

        if (selected_card["rarity"] == RARITY_TIERS[-1] and
            selected_card["border"] == BORDER_TIERS[-1] and
                selected_card["image_quality"] == QUALITY_TIERS[-1]):
            print(
                f"{Fore.YELLOW}This card is fully maxed out! (Legendary | Rainbow | Perfect){Fore.RESET}")
            return

        # Select upgrade type
        print("\nWhat would you like to upgrade?")
        print("1. Rarity")
        print("2. Border")
        print("3. Image Quality")
        upgrade_choice = input("Select upgrade type (0 to cancel): ").strip()

        if upgrade_choice == "0":
            time.sleep(2)
            return

        upgrade_map = {
            "1": ("rarity", RARITY_TIERS),
            "2": ("border", BORDER_TIERS),
            "3": ("image_quality", QUALITY_TIERS)
        }

        if upgrade_choice not in upgrade_map:
            print(f"{Fore.RED}Invalid choice.{Fore.RESET}")
            time.sleep(2)
            return

        card_key, tiers = upgrade_map[upgrade_choice]
        current_value = selected_card[card_key]

        # Check if already max tier
        if current_value == tiers[-1]:
            print(
                f"{Fore.YELLOW}{card_key.capitalize()} is already at max tier ({tiers[-1]})!{Fore.RESET}")
            return

        # Get next tier and cost
        current_index = tiers.index(current_value)
        next_tier = tiers[current_index + 1]
        cost = UPGRADE_COSTS[current_index + 1]
        cost_items = cost["items"]
        cost_coins = cost["coins"]

        # Show upgrade preview
        cost_str = ", ".join(f"{qty} {item}" for item,
                             qty in cost_items.items())
        print(
            f"\nUpgrade: {current_value} → {Fore.GREEN}{next_tier}{Fore.RESET}")
        print(f"Cost: {cost_str} + {cost_coins} coins")
        confirm = input("Confirm upgrade? (y/n): ").strip().lower()

        if confirm != "y":
            print("Upgrade cancelled.")
            time.sleep(2)
            return

        if next_tier == "Rainbow" or "Perfect" and level_req is False:
            print(
                f"You are not eligible for this upgrade. Your current level is {exp}. Requirement is Level 10 and above.")
            time.sleep(2)
            return
        elif next_tier == "Rainbow" or "Perfect" and upd_type == 0:
            print(
                "You are currently in basic upgrading mode. Switch to Advanced and try again.")
            time.sleep(2)
            return

        # Check coins
        if p_coins < cost_coins:
            print(
                f"{Fore.RED}Not enough coins! You have {p_coins} but need {cost_coins}.{Fore.RESET}")
            time.sleep(2)
            return

        # Check items
        item_filepath = "Database/itemdata.json"
        existing_items = []
        if os.path.exists(item_filepath):
            with open(item_filepath, "r") as f:
                content = f.read()
                if content.strip():
                    existing_items = json.loads(content)

        for required_item, required_qty in cost_items.items():
            for owned_item in existing_items:
                if owned_item["item_name"] == required_item:
                    if owned_item["quantity"] < required_qty:
                        print(
                            f"{Fore.RED}Not enough {required_item}! You have {owned_item['quantity']} but need {required_qty}.{Fore.RESET}")
                        time.sleep(2)
                        return
                    time.sleep(1)
                    break
            else:
                print(f"{Fore.RED}You don't have any {required_item}!{Fore.RESET}")
                time.sleep(2)
                return

        # Deduct coins
        self.spend_money(cost_coins)

        # Deduct items
        for item_name, qty in cost_items.items():
            for owned_item in existing_items:
                if owned_item["item_name"] == item_name:
                    owned_item["quantity"] -= qty
                    break
        existing_items = [
            item for item in existing_items if item["quantity"] > 0]
        with open(item_filepath, "w") as f:
            json.dump(existing_items, f, indent=4)

        # Apply upgrade
        selected_card[card_key] = next_tier

        # Recalculate worth
        new_worth = (
            RARITY_WORTH[selected_card["rarity"]] *
            BORDER_WORTH[selected_card["border"]] *
            QUALITY_WORTH[selected_card["image_quality"]]
        )
        selected_card["worth"] = round(new_worth, 2)

        # Save updated cards
        with open(filepath, "w") as f:
            json.dump(cards, f, indent=4)

        print(f"\n{Fore.GREEN}Upgrade successful!{Fore.RESET}")
        print(f"{selected_card['name']} | Rarity: {selected_card['rarity']} | Border: {selected_card['border']} | Quality: {selected_card['image_quality']} | Worth: ${selected_card['worth']:.2f}")
        time.sleep(2)
        input("Press ENTER to continue...")

    def claim_daily(self, Cpack, Ipack):
        filepath = "Database/dailydata.json"
        os.makedirs("Database", exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")

        # Load existing data
        existing_data = {"last_claimed": None}
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
                if content.strip():
                    existing_data = json.loads(content)

        # Check if already claimed today
        if existing_data["last_claimed"] == today:
            print(
                f"{Fore.YELLOW}You've already claimed your daily reward today!{Fore.RESET}")
            print(f"{Fore.YELLOW}Come back tomorrow for another reward!{Fore.RESET}")
            time.sleep(2)
            return

        print(f"{Fore.CYAN}=== DAILY REWARD ==={Fore.RESET}")
        print("Opening your daily reward...")
        time.sleep(1.5)

        # Randomly pick a reward tier
        reward_tiers = [
            {
                "name": "Small",
                "coins": random.randint(10, 30),
                "exp": random.randint(10, 30),
                "items": {random.choice(["Magical Powder", "Fiery Leather"]): random.randint(1, 3)},
                "cards": 0
            },
            {
                "name": "Medium",
                "coins": random.randint(30, 70),
                "exp": random.randint(30, 60),
                "items": {random.choice(["Quantum Ball", "Astral Wand"]): random.randint(1, 2)},
                "cards": 1
            },
            {
                "name": "Large",
                "coins": random.randint(70, 150),
                "exp": random.randint(60, 100),
                "items": {
                    random.choice(["Void Crystal", "Celestial Wand"]): 1,
                    random.choice(["Magical Powder", "Quantum Ball"]): random.randint(2, 5)
                },
                "cards": 2
            }
        ]

        # Weighted random tier selection
        tier = random.choices(
            reward_tiers,
            weights=[50, 35, 15],  # Small=50%, Medium=35%, Large=15%
            k=1
        )[0]

        print(f"{Fore.CYAN}You got a {tier['name']} reward!{Fore.RESET}\n")

        # Give coins
        self.add_coins(tier["coins"])

        # Give EXP
        self.gain_exp(tier["exp"])

        # Give items
        self.auto_addItems(tier["items"])
        for item_name, qty in tier["items"].items():
            print(f"{Fore.GREEN}+{qty} {item_name}{Fore.RESET}")

        # Give card packs
        if tier["cards"] > 0:
            print(
                f"\n{Fore.CYAN}Opening {tier['cards']} card pack(s)...{Fore.RESET}")
            for _ in range(tier["cards"]):
                time.sleep(1)
                cards, x = Cpack.open_pack()
                self.add_cards(cards)
                for card in cards:
                    print(f"{Fore.GREEN}+{card.name} ({card.rarity}){Fore.RESET}")

        # Save claimed date
        existing_data["last_claimed"] = today
        with open(filepath, "w") as f:
            json.dump(existing_data, f, indent=4)

        print(f"\n{Fore.CYAN}=== REWARD CLAIMED! ==={Fore.RESET}")
        print("Come back tomorrow for another reward!")
        time.sleep(2)

    def show_about(self):
        print("\n=== ABOUT POKEPY ===")
        print("Game        : PokePy")
        print("Version     : v2.1.0")
        print("Developer   : JL (PyDevelopments)")
        print("Description : A terminal-based card game.")
        print()
        print("=== VERSION HISTORY ===")
        print("v2.0.0-alpha: Card upgrade system, daily rewards")
        print("v2.0.0-beta : Special events, bug fixes, exe packaging")
        print("v2.0.0      : Stable release")
        print("v2.1.0      : Sounds, Stats, Upgrades, Limits, Mass Inputs")
        print(
            "v2.2.0      : Release -> Apr 27, 2026 | 3:00 PM PhST (Estimate, might extend.)")
        print("====================\n")
        time.sleep(2)
        print("\n=== CREDITS ===")
        print("Wait for v2.2.0!")

    def trade_sell_cards(self):
        filepath = "Database/carddata.json"
        trade_filepath = "Database/tradedata.json"
        os.makedirs("Database", exist_ok=True)

        if not os.path.exists(filepath):
            print("No card collection found.")
            time.sleep(2)
            return

        with open(filepath, "r") as f:
            content = f.read()
            if not content.strip():
                print("Your card collection is empty.")
                time.sleep(2)
                return
            cards = json.loads(content)

        # Load trade data
        today = datetime.now().strftime("%Y-%m-%d")
        trade_data = {"date": today, "trades_left": 3}
        if os.path.exists(trade_filepath):
            with open(trade_filepath, "r") as f:
                content = f.read()
                if content.strip():
                    trade_data = json.loads(content)
                    # Reset if it's a new day
                    if trade_data["date"] != today:
                        trade_data = {"date": today, "trades_left": 3}

        print("\n=== CARD TRADING & SELLING ===")
        print("1. Sell a card for coins")
        print(
            f"2. Trade a card with BOT ({trade_data['trades_left']}/3 trades left today)")
        opt = input("Choose an option (0 to cancel): ").strip()

        if opt == "0":
            time.sleep(2)
            return

        # Show collection
        print("\nYour Card Collection:")
        for i, card in enumerate(cards, start=1):
            print(
                f"{i}. {card['name']} | Rarity: {card['rarity']} | Border: {card['border']} | Quality: {card['image_quality']} | Worth: ${card['worth']:.2f}")
        print()

        if opt == "1":
            print("Enter card number/s to sell separated by commas (e.g. 1,3,5 ): ")
            raw = input("Select cards (0 to cancel): ")

            if raw == "0":
                print("Canceled")
                time.sleep(2)
                return

            # Parse input
            try:
                choices = [int(x.strip()) for x in raw.split(",")]
            except ValueError:
                print("Invalid Input. Use numbers separated by commas")
                time.sleep(2)
                return

            # Validate Choices
            invalid = [c for c in choices if c < 1 or c > len(cards)]
            if invalid:
                print(f"Invalid card numbers: {invalid}")
                time.sleep(2)
                return

            # Remove Duplicates
            choice = list(set(choices))

            # Show selected cards and total sell price
            selected_cards = [cards[c - 1] for c in choices]
            total_sell = round(
                sum(card["worth"] * 0.75 for card in selected_cards), 2)

            print(f"\nSelected Cards:")
            for card in selected_cards:
                sell_price = round(card["worth"] * 0.75, 2)
                print(f" - {card['name']} -> ${sell_price}")
            print(f"Total sell price: ${total_sell}")

            conf = input("Confirm sell? (y/n): ").strip().lower()
            if conf != "y":
                print("Sell cancelled.")
                time.sleep(2)
                return

            # Remove sold cards (remove in reverse order to avoid index shifting)
            for i in sorted([c - 1 for c in choices], reverse=True):
                cards.pop(i)

            with open(filepath, "w") as f:
                json.dump(cards, f, indent=4)

            self.add_coins(int(total_sell))
            print(
                f"{Fore.GREEN}Successfully sold {len(choices)} card(s) for ${total_sell}!{Fore.RESET}")

        elif opt == "2":
            # Check trades left
            if trade_data["trades_left"] <= 0:
                print(
                    f"{Fore.RED}No trades left today! Come back tomorrow.{Fore.RESET}")
                time.sleep(2)
                return

            # Select card to trade away
            try:
                choice = int(
                    input("Select a card to trade away (0 to cancel): "))
                if choice == 0:
                    time.sleep(2)
                    return
                if choice < 1 or choice > len(cards):
                    print("Invalid choice.")
                    time.sleep(2)
                    return
            except ValueError:
                print("Please enter a valid number.")
                time.sleep(2)
                return

            your_card = cards[choice - 1]

            # Generate random Bot card
            npc_rarities = {
                "Common": ["Common Balbuzer", "Common Spookie", "Common Fireguard"],
                "Uncommon": ["Uncommon Dreamy", "Uncommon Jiggleboo", "Uncommon Peckoo"],
                "Rare": ["Rare Pikagloo", "Rare Grengie", "Rare Mewmew"],
                "Legendary": ["Legendary Fireguard", "Legendary Dragoneer"]
            }
            npc_borders = ["Non-Holo", "Foil", "Holo", "Rainbow"]
            npc_qualities = ["Poor", "Good", "Excellent", "Perfect"]

            npc_rarity = random.choice(list(npc_rarities.keys()))
            npc_name = random.choice(npc_rarities[npc_rarity])
            npc_border = random.choice(npc_borders)
            npc_quality = random.choice(npc_qualities)
            npc_worth = round(
                RARITY_WORTH[npc_rarity] *
                BORDER_WORTH[npc_border] *
                QUALITY_WORTH[npc_quality], 2
            )

            npc_card = {
                "name": npc_name,
                "rarity": npc_rarity,
                "border": npc_border,
                "image_quality": npc_quality,
                "worth": npc_worth
            }

            print(
                f"\nYou are trading: {your_card['name']} (Worth: ${your_card['worth']:.2f})")
            print(f"\nNPC offers: {npc_card['name']}")
            print(f"  Rarity  : {npc_card['rarity']}")
            print(f"  Border  : {npc_card['border']}")
            print(f"  Quality : {npc_card['image_quality']}")
            print(f"  Worth   : ${npc_card['worth']:.2f}")

            if npc_worth < your_card["worth"]:
                print(
                    f"{Fore.YELLOW}Warning! Bot's card is worth less than yours!{Fore.RESET}")

            confirm = input("\nAccept trade? (y/n): ").strip().lower()
            if confirm != "y":
                print("Trade cancelled.")
                return

            # Swap cards
            cards[choice - 1] = npc_card
            with open(filepath, "w") as f:
                json.dump(cards, f, indent=4)

            # Update trades left
            trade_data["trades_left"] -= 1
            with open(trade_filepath, "w") as f:
                json.dump(trade_data, f, indent=4)

            print(
                f"{Fore.GREEN}Successfully traded {your_card['name']} for {npc_card['name']}!{Fore.RESET}")
            print(
                f"{Fore.YELLOW}{trade_data['trades_left']}/3 trades remaining today.{Fore.RESET}")

        else:
            print("Invalid option.")

    def startup(self):
        global startup
        startup = datetime.now().strftime("%H:%M:%S")
        print(f"Your startup time is: {startup}")
        time.sleep(1)
        pass

    def show_card_stats(self):
        filepath = "Database/carddata.json"

        if not os.path.exists(filepath):
            print("No card collection found.")
            time.sleep(2)
            return

        with open(filepath, "r") as f:
            content = f.read()
        if not content.strip():
            print("Your card collection is empty.")
            time.sleep(2)
            return
        cards = json.loads(content)

        if not cards:
            print("Your card collection is empty.")
            time.sleep(2)
            return

        # Count breakdowns
        rarity_count = {}
        border_count = {}
        quality_count = {}
        total_worth = 0
        most_valuable = cards[0]
        rarest_card = cards[0]
        rarity_order = ["Common", "Uncommon", "Rare", "Legendary"]

        for card in cards:
            r = card["rarity"]
            rarity_count[r] = rarity_count.get(r, 0) + 1

            b = card["border"]
            border_count[b] = border_count.get(b, 0) + 1

            q = card["image_quality"]
            quality_count[q] = quality_count.get(q, 0) + 1

            total_worth += card["worth"]

            if card["worth"] > most_valuable["worth"]:
                most_valuable = card

            if rarity_order.index(card["rarity"]) > rarity_order.index(rarest_card["rarity"]):
                rarest_card = card

        # Print terminal stats
        print("\n=== CARD COLLECTION STATISTICS ===")
        print(f"Total Cards      : {len(cards)}")
        print(f"Total Worth      : ${total_worth:.2f}")
        print(
            f"\nMost Valuable    : {most_valuable['name']} (${most_valuable['worth']:.2f})")
        print(
            f"Rarest Card      : {rarest_card['name']} ({rarest_card['rarity']})")

        print(f"\n--- Rarity Breakdown ---")
        for rarity in rarity_order:
            count = rarity_count.get(rarity, 0)
            pct = (count / len(cards)) * 100
            bar = "█" * int(pct / 5)
            print(f"{rarity:<12}: {bar:<20} {count} ({pct:.1f}%)")

        print(f"\n--- Border Breakdown ---")
        border_order = ["Non-Holo", "Foil", "Holo", "Rainbow"]
        for border in border_order:
            count = border_count.get(border, 0)
            pct = (count / len(cards)) * 100
            bar = "█" * int(pct / 5)
            print(f"{border:<12}: {bar:<20} {count} ({pct:.1f}%)")

        print(f"\n--- Quality Breakdown ---")
        quality_order = ["Poor", "Good", "Excellent", "Perfect"]
        for quality in quality_order:
            count = quality_count.get(quality, 0)
            pct = (count / len(cards)) * 100
            bar = "█" * int(pct / 5)
            print(f"{quality:<12}: {bar:<20} {count} ({pct:.1f}%)")

        print("===================================\n")

        # Ask to show graph
        show_graph = input("Show visual graph? (y/n): ").strip().lower()
        if show_graph != "y":
            print("Returning...")
            time.sleep(2)
            return

        # Generate graph
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle("Card Collection Statistics",
                     fontsize=16, fontweight="bold")

        # Rarity pie chart
        rarity_labels = [k for k in rarity_order if k in rarity_count]
        rarity_values = [rarity_count[k] for k in rarity_labels]
        rarity_colors = ["#a8d8a8", "#7ec8e3", "#c8a8e8", "#f4c875"]
        axes[0].pie(rarity_values, labels=rarity_labels,
                    colors=rarity_colors, autopct="%1.1f%%", startangle=90)
        axes[0].set_title("Rarity Breakdown")

        # Border bar chart
        border_labels = [b for b in border_order if b in border_count]
        border_values = [border_count[b] for b in border_labels]
        border_colors = ["#d3d3d3", "#c8e6c9", "#b3d9f5", "#f4c875"]
        axes[1].bar(border_labels, border_values,
                    color=border_colors[:len(border_labels)])
        axes[1].set_title("Border Breakdown")
        axes[1].set_ylabel("Count")

        # Quality bar chart
        quality_labels = [q for q in quality_order if q in quality_count]
        quality_values = [quality_count[q] for q in quality_labels]
        quality_colors = ["#ef9a9a", "#ffcc80", "#a5d6a7", "#80cbc4"]
        axes[2].bar(quality_labels, quality_values,
                    color=quality_colors[:len(quality_labels)])
        axes[2].set_title("Quality Breakdown")
        axes[2].set_ylabel("Count")

        plt.tight_layout()
        plt.savefig("Database/card_stats.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"{Fore.GREEN}Graph saved! Opening...{Fore.RESET}")

        # Open the image automatically
        import subprocess
        subprocess.Popen(["start", "Database/card_stats.png"], shell=True)


class Shop:
    def __init__(self):
        self.stocklist = ["ON STOCK", "NO STOCK"]
        self.randchoice = random.choice(self.stocklist)

    def verify(self, buy, inv):
        # buy = the item the player wants to buy (string)
        # inv = dict of items the player needs to spend e.g. {"Astral Wand": 2}

        filepath = "Database/itemdata.json"
        existing_data = []

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
                if content.strip():
                    existing_data = json.loads(content)

        # Check if player has enough of each required item
        for required_item, required_qty in inv.items():
            for owned_item in existing_data:
                if owned_item["item_name"] == required_item:
                    if owned_item["quantity"] < required_qty:
                        print(
                            f"{Fore.RED}Not enough {required_item}! You have {owned_item['quantity']} but need {required_qty}.{Fore.RESET}")
                        time.sleep(2)
                        return False
                    break
            else:
                # Item not found in inventory at all
                print(f"{Fore.RED}You don't have any {required_item}!{Fore.RESET}")
                time.sleep(2)
                return False

        print(f"{Fore.GREEN}Purchase verified! You can buy {buy}.{Fore.RESET}")
        time.sleep(2)
        return True

    def cts(self, p, events, active_event):
        print("Welcome to the Shop, player!\n")
        print("CURRENT STOCKS")
        print(f"1. Obsidian Shard     - 20 Magical Powder, 10 Fiery Leather, and 2 Void Crystal")
        print(f"2. Upgrade Card       - 1 Quantum Ball, 10 Magical Powder")
        print(f"3. Chest              - 3 Magical Powder, 5 Fiery Leather")
        print(f"4. Celestial Wand     - {self.randchoice}")
        print()

        if self.randchoice == "ON STOCK":
            print(
                f"Celestial Wand costs: 5 Fiery Leather, 5 Magical Powder, 4 Quantum Ball, 1 Astral Wand and 1 Obsidian Shard.\n")

        # Show limited items if Flash Sale is active
        limited = events.get_limited_shop_items(active_event)
        if limited:
            print(f"{Fore.CYAN}=== FLASH SALE - LIMITED ITEMS ==={Fore.RESET}")
            for i, (item_name, details) in enumerate(limited.items(), start=5):
                cost_str = ", ".join(f"{qty} {item}" for item,
                                     qty in details["cost"].items())
                print(f"{i}. {item_name} - {cost_str}")
            print()

        # Define shop items
        shop_items = {
            "1": {"name": "Obsidian Shard", "cost": {"Magical Powder": 20, "Fiery Leather": 10, "Void Crystal": 2}},
            "2": {"name": "Upgrade Card", "cost": {"Quantum Ball": 1, "Magical Powder": 10}},
            "3": {"name": "Chest", "cost": {"Magical Powder": 3, "Fiery Leather": 5}},
            "4": {"name": "Celestial Wand", "cost": {"Fiery Leather": 5, "Magical Powder": 5, "Quantum Ball": 4, "Obsidian Shard": 1, "Astral Wand": 1}}
        }

        inp = input("Please select an item to trade: ")

        # Handle limited shop items
        if limited:
            limited_keys = {str(i): name for i, name in enumerate(
                limited.keys(), start=5)}
            if inp in limited_keys:
                limited_name = limited_keys[inp]
                limited_details = limited[limited_name]

                cost_str = ", ".join(f"{qty} {item}" for item,
                                     qty in limited_details["cost"].items())
                print(f"\nYou selected: {limited_name}")
                print(f"Cost: {cost_str}")

                try:
                    qty = int(
                        input("How many do you want to buy? (1-10): ").strip())
                    if qty < 1 or qty > 10:
                        print("Invalid Quantity.")
                        time.sleep(2)
                        return
                except ValueError:
                    print("Invalid quantity.")
                    time.sleep(2)
                    return

                total_cost = {item: amount * qty for item,
                              amount in limited_details["cost"].items()}
                total_cost_str = ", ".join(
                    f"{amount} {item}" for item, amount in total_cost.items())
                print(f"Total cost for {qty}x: {total_cost_str}")
                confirm = input("Confirm buy? (y/n): ").strip().lower()

                if confirm != "y":
                    print("Trade cancelled.")
                    time.sleep(2)
                    return

                if not self.verify(limited_name, total_cost):
                    time.sleep(2)
                    return

                self.deduct_items(total_cost)
                for _ in range(qty):
                    p.auto_addItems(limited_details["reward"])
                    print(
                        f"{Fore.GREEN}You successfully bought {qty}x {limited_name}!{Fore.RESET}")
                time.sleep(3)
                return

        # Handle regular shop items
        if inp not in shop_items:
            print("Item not found. Try again!")
            time.sleep(2)
            return

        if inp == "4" and self.randchoice == "NO STOCK":
            print(
                f"{Fore.RED}Celestial Wand is not on stock. Try again later!{Fore.RESET}")
            time.sleep(2)
            return

        selected = shop_items[inp]
        name = selected["name"]
        cost = selected["cost"]

        # Ask quantity
        try:
            qty = int(input(f"How many {name} do you want? (1-10): ").strip())
            if qty < 1 or qty > 10:
                print("Invalid quantity.")
                time.sleep(2)
                return
        except ValueError:
            print("Invalid quantity.")
            time.sleep(2)
            return

        # Multiply cost by quantity
        total_cost = {item: amount * qty for item, amount in cost.items()}
        cost_str = ", ".join(f"{amount} {item}" for item,
                             amount in total_cost.items())
        print(f"\nYou Selected: {qty}x {name}")
        print(f"Total cost: {cost_str}")
        confirm = input("Confirm buy? (y/n): ").strip().lower()

        if confirm != "y":
            print("Trade cancelled.")
            time.sleep(2)
            return

        if not self.verify(name, cost):
            time.sleep(2)
            return

        if inp == "3":
            self.deduct_items(total_cost)
            for _ in range(qty):
                self.open_chest(p, active_event)
                time.sleep(1)
                return

        self.deduct_items(total_cost)
        for _ in range(qty):
            p.auto_addItems({name: 1})
            print(f"{Fore.GREEN}You successfully bought {qty}x {name}!{Fore.RESET}")

    def deduct_items(self, cost):
        filepath = "Database/itemdata.json"
        existing_data = []

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
                if content.strip():
                    existing_data = json.loads(content)

        for item_name, qty in cost.items():
            for owned_item in existing_data:
                if owned_item["item_name"] == item_name:
                    owned_item["quantity"] -= qty
                    break

        # Remove items with 0 or less quantity
        existing_data = [
            item for item in existing_data if item["quantity"] > 0]

        with open(filepath, "w") as f:
            json.dump(existing_data, f, indent=4)

    def open_chest(self, p, event=None):
        print(f"\n{Fore.YELLOW}Opening chest...{Fore.RESET}")
        time.sleep(1.5)

        # Loot pool with weights — lower weight = rarer
        loot_pool = [
            {"name": "Magical Powder", "weight": 40},
            {"name": "Fiery Leather", "weight": 30},
            {"name": "Quantum Ball", "weight": 20},
            {"name": "Void Crystal", "weight": 7},  # rare exclusive
        ]

        names = [item["name"] for item in loot_pool]
        weights = [item["weight"] for item in loot_pool]

        # Random amount of random items (1-5)
        num_items = random.randint(1, 5)
        loot = random.choices(names, weights=weights, k=num_items)

        # Count duplicates
        loot_counts = {}
        for item in loot:
            loot_counts[item] = loot_counts.get(item, 0) + 1

        if event:
            loot_counts = SpecialEvents().apply_rare_drops(loot_counts, event)

        # Display loot
        print(f"{Fore.YELLOW}You got:{Fore.RESET}")
        for item_name, qty in loot_counts.items():
            if item_name == "Void Crystal":
                print(f"{Fore.MAGENTA}  - {item_name} x{qty} (RARE!){Fore.RESET}")
            else:
                print(f"  - {item_name} x{qty}")

        time.sleep(1)

        p.auto_addItems(loot_counts)
        print(f"{Fore.GREEN} Items added to your inventory!{Fore.RESET}")


class SpecialEvents:
    def __init__(self):
        self.filepath = "Database/eventdata.json"
        os.makedirs("Database", exist_ok=True)

    def _load_event(self):
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath, "r") as f:
            content = f.read()
            if content.strip():
                return json.loads(content)
        return None

    def _save_event(self, event_data):
        with open(self.filepath, "w") as f:
            json.dump(event_data, f, indent=4)

    def check_event(self):
        existing = self._load_event()
        now = datetime.now()

        # Check if current event is still active
        if existing and existing.get("active"):
            end_time = datetime.strptime(
                existing["end_time"], "%Y-%m-%d %H:%M:%S")
            if now < end_time:
                return existing  # event still running
            else:
                # Event expired
                print(
                    f"{Fore.YELLOW}The {existing['name']} event has ended!{Fore.RESET}")
                existing["active"] = False
                self._save_event(existing)

        # Random chance to trigger a new event (30% chance per day)
        if random.random() < 0.30:
            return self.start_event()

        return None

    def start_event(self):
        # Pick random event and duration
        event = random.choice(SPECIAL_EVENTS)
        duration_key = random.choice(["short", "medium", "long"])
        duration_days = EVENT_DURATIONS[duration_key]

        now = datetime.now()
        end_time = now + timedelta(days=duration_days)

        duration_display = {
            "short": "1 hour",
            "medium": "24 hours",
            "long": "3 days"
        }

        event_data = {
            "name": event["name"],
            "type": event["type"],
            "description": event["description"],
            "duration": duration_display[duration_key],
            "start_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "active": True,
            "data": event
        }

        self._save_event(event_data)

        print(f"\n{Fore.CYAN}=== SPECIAL EVENT STARTED ==={Fore.RESET}")
        print(f"{Fore.CYAN}{event['name']}{Fore.RESET}")
        print(f"{event['description']}")
        print(f"Duration: {duration_display[duration_key]}")
        print(f"{Fore.CYAN}============================={Fore.RESET}\n")
        time.sleep(2)

        return event_data

    def show_active_event(self):
        existing = self._load_event()
        if not existing or not existing.get("active"):
            print(f"{Fore.YELLOW}No special event is currently active.{Fore.RESET}")
            return

        now = datetime.now()
        end_time = datetime.strptime(existing["end_time"], "%Y-%m-%d %H:%M:%S")

        if now >= end_time:
            print(f"{Fore.YELLOW}No special event is currently active.{Fore.RESET}")
            return

        remaining = end_time - now
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)

        print(f"\n{Fore.CYAN}=== ACTIVE EVENT ==={Fore.RESET}")
        print(f"Event    : {existing['name']}")
        print(f"Details  : {existing['description']}")
        print(f"Time left: {hours}h {minutes}m")
        print(f"{Fore.CYAN}===================={Fore.RESET}\n")
        time.sleep(2)

    def apply_bonus_coins(self, amount, event):
        if event and event["type"] == "bonus_coins":
            multiplier = event["data"]["multiplier"]
            bonus = amount * (multiplier - 1)
            print(f"{Fore.CYAN}Coin Frenzy! +{bonus} bonus coins!{Fore.RESET}")
            return amount * multiplier
        return amount

    def apply_rare_drops(self, loot_counts, event):
        if event and event["type"] == "rare_items":
            bonus = event["data"]["bonus_items"]
            for item, qty in bonus.items():
                loot_counts[item] = loot_counts.get(item, 0) + qty
                print(f"{Fore.CYAN}Rare Drop Festival! +{qty} {item}!{Fore.RESET}")
        return loot_counts

    def get_limited_shop_items(self, event):
        if event and event["type"] == "limited_shop":
            return event["data"]["limited_items"]
        return {}


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.settings_filepath = "Database/settings.json"
        os.makedirs("Database", exist_ok=True)
        pygame.mixer.init()
        self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.settings_filepath):
            self._save_settings()
            return
        with open(self.settings_filepath, "r") as f:
            content = f.read()
            if content.strip():
                data = json.loads(content)
                self.enabled = data.get("sound_enabled", True)

    def _save_settings(self):
        with open(self.settings_filepath, "w") as f:
            json.dump({"sound_enabled": self.enabled}, f, indent=4)

    def toggle_sound(self):
        self.enabled = not self.enabled
        self._save_settings()
        status = "ON" if self.enabled else "OFF"
        print(f"{Fore.CYAN}Sound turned {status}!{Fore.RESET}")
        time.sleep(1)

    def play_bgm(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.load("Sounds/bgm.mp3")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)  # -1 loops forever
        except Exception:
            pass  # silently fail if file missing

    def stop_bgm(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def play_sfx(self, sound_file):
        if not self.enabled:
            return
        try:
            sound = pygame.mixer.Sound(f"Sounds/{sound_file}")
            sound.set_volume(0.7)
            sound.play()
        except Exception:
            pass  # silently fail if file missing


class Settings:
    def show(self, sound_manager):
        while True:
            print("\n=== SETTINGS ===")
            sound_status = "ON" if sound_manager.enabled else "OFF"
            print(f"1. Sound         [{sound_status}]")
            print(f"2. Display")        # future
            print(f"3. Gameplay")       # future
            print(f"4. Account")        # future
            print(f"5. Back")
            print("================\n")

            opt = input("Choose an option: ").strip()

            if opt == "1":
                self.sound_settings(sound_manager)
            elif opt == "5":
                return
            else:
                print("Coming soon!")
                time.sleep(1)

    def sound_settings(self, sound_manager):
        while True:
            print("\n=== SOUND SETTINGS ===")
            sound_status = "ON" if sound_manager.enabled else "OFF"
            print(f"1. Toggle Sound  [{sound_status}]")
            print(f"2. Back")
            print("======================\n")

            opt = input("Choose an option: ").strip()

            if opt == "1":
                sound_manager.toggle_sound()
            elif opt == "2":
                return
            else:
                print("Invalid option.")
                time.sleep(1)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def log_error(error, location="Unknown"):
    os.makedirs("Database/upds", exist_ok=True)
    filepath = "Database/upds/Pokepy Logs.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filepath, "a") as f:
        f.write(f"[{timestamp}] ERROR in {location}:\n")
        f.write(f"{traceback.format_exc()}\n")
        f.write("-" * 50 + "\n")

    print(f"{Fore.RED}Something went wrong! The error has been logged.{Fore.RESET}")
    print(f"{Fore.RED}Please report this to lugasan.pydevelopments@gmail.com{Fore.RESET}")
    time.sleep(2)


# MAIN

def main():
    Cpack = Pack()
    p = Player()
    Ipack = ItemPack()
    shop = Shop()
    events = SpecialEvents()
    sound_manager = SoundManager()
    settings = Settings()
    active_event = events.check_event()
    p.load_progress()
    p.startup()
    sound_manager.play_bgm()
    while True:
        clear_screen()
        print("Hello! Welcome to Pokepy by PyDevelopments! Version 2.1.0")
        time.sleep(2)
        print(
            "1. Open a pack\n"
            "2. Player Stats\n"
            "3. View Inventory/Collection\n"
            "4. Daily Reward\n"
            "5. Modify Cards\n"
            "6. Special Events\n"
            "7. Shop\n"
            "8. Card Trade & Selling\n"
            "9. Card Statistics (NEW!)\n"
            "10. About & Credits\n"
            "11. Settings (NEW!)\n"
            "12. Exit"
        )
        try:
            x = input("Choose an option: ")
            if x == '1':
                print(
                    "1. Card Pack\n"
                    "2. Item Pack\n"
                )
                c = input("Choose a pack: ")
                if c == '1':
                    sound_manager.play_sfx("pack_open.mp3")
                    Cpack.verify()
                    cards, pack_value = Cpack.open_pack()
                    print("Nice! You opened a pack. Here's what you got:")
                    time.sleep(2)
                    for i, card in enumerate(cards):
                        print(f"{i+1}. {card}")
                    print(f"Total pack value: ${pack_value}")
                    time.sleep(2)
                    p.add_cards(cards)
                    time.sleep(1)
                    p.gain_exp(150)
                    coins1 = events.apply_bonus_coins(200, active_event)
                    p.add_coins(coins1)
                    print()  # Blank Line
                    input("Press ENTER to continue...")
                elif c == '2':
                    item = Ipack.open_Ipack()
                    sound_manager.play_sfx("pack_open.mp3")
                    print("Nice! Here are the items you got:")
                    time.sleep(1.5)
                    item_counts = {}
                    for x, items in enumerate(item):
                        print(f"{x+1}. {items.Icard}")
                    for card in item:
                        name = card.Icard
                        item_counts[name] = item_counts.get(name, 0) + 1
                    print("You may use these items to upgrade your cards.")
                    p.gain_exp(50)
                    coins2 = events.apply_bonus_coins(100, active_event)
                    p.add_coins(coins2)
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
                p.claim_daily(Cpack, Ipack)
            elif x == "5":
                coins_filepath = "Database/coinsdata.json"
                current_coins = 0
                if os.path.exists(coins_filepath):
                    with open(coins_filepath, "r") as f:
                        content = f.read()
                        if content.strip():
                            current_coins = json.loads(content)["coins"]

                p.upgrade_card(current_coins)
            elif x == "6":
                events.show_active_event()

                if active_event and active_event["type"] == "limited shop":
                    print(
                        f"{Fore.CYAN}Flash Sale is active! Visit the shop to see limited items!")
                    go_shop = input("Go to shop now? (y/n): ").strip().lower()
                    if go_shop == "y":
                        shop.cts(p, events, active_event)
                    else:
                        print(active_event["type"])

                input("Press ENTER to continue...")
            elif x == "7":
                shop.cts(p, events, active_event)
                input("Press ENTER to continue...")
            elif x == "8":
                p.trade_sell_cards()
                time.sleep(2)
                input("Press ENTER to continue...")
            elif x == "9":
                p.show_card_stats()
                input("Press ENTER to continue...")
            elif x == "10":
                p.show_about()
                time.sleep(2)
                input("Press ENTER to continue...")
            elif x == "11":
                settings.show(sound_manager)
            elif x == "12":
                print("Thank you for playing! See you again!")
                sound_manager.stop_bgm()
                time.sleep(2)
                sys.exit()
        except (Exception, KeyboardInterrupt) as e:
            log_error(e, location=f"Menu option {x}")
            input("Press ENTER to restart...")
            time.sleep(2)


if __name__ == '__main__':
    main()
