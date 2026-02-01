from django.core.management.base import BaseCommand
from store.models import Product
import requests
import random

class Command(BaseCommand):
    help = 'Downloads Raw JSON from GitHub (Bypasses ALL API Limits)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old Pokemon data...")
        Product.objects.filter(game='PKM').delete()

        # These are the raw file codes for the sets you want.
        # base1 = Base Set
        # sv3pt5 = Scarlet & Violet 151
        # sv4 = Paradox Rift
        # swsh7 = Evolving Skies
        TARGET_SETS = ["base1", "sv3pt5", "sv4", "swsh7"]
        
        # GitHub Raw Data URL (The Source of Truth)
        GITHUB_BASE = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/cards/en/"

        # --- RARITY PRICING ENGINE ---
        # Since we can't query live prices (blocked), we estimate based on rarity.
        # This allows your Deck Builder to function with realistic "Costs".
        PRICE_MAP = {
            "Common": (0.10, 0.50),
            "Uncommon": (0.50, 1.50),
            "Rare": (1.50, 4.00),
            "Rare Holo": (10.00, 25.00),
            "Rare Holo GX": (5.00, 15.00),
            "Rare Holo V": (2.00, 8.00),
            "Rare Holo VMAX": (8.00, 25.00),
            "Rare Secret": (20.00, 80.00),
            "Rare Ultra": (15.00, 50.00),
            "Illustration Rare": (15.00, 45.00),
            "Special Illustration Rare": (30.00, 150.00),
            "Hyper Rare": (15.00, 40.00)
        }

        # Specific Overrides for the Big Hitters (to make the store look reputable)
        # We look for these names and force a high price.
        GOD_TIER_CARDS = {
            "Charizard": 150.00,
            "Blastoise": 80.00,
            "Venusaur": 70.00,
            "Umbreon VMAX": 650.00, # Moonbreon
            "Giratina V": 250.00,
            "Mewtwo": 45.00
        }

        def fetch_set_from_github(set_code):
            url = f"{GITHUB_BASE}{set_code}.json"
            self.stdout.write(f"\nDownloading {set_code}.json from GitHub...")
            
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Failed to download {set_code}"))
                    return

                cards = response.json()
                self.stdout.write(f"Processing {len(cards)} cards...")
                
                batch = []
                for card in cards:
                    try:
                        name = card.get('name', 'Unknown')
                        rarity = card.get('rarity', 'Common')
                        
                        # 1. IMAGE LOGIC
                        # The GitHub data usually has images.small and images.large
                        image_url = ""
                        if 'images' in card:
                            image_url = card['images'].get('small') or card['images'].get('large')
                        
                        if not image_url:
                            continue # Skip if absolutely no image

                        # 2. PRICE LOGIC
                        # Check God Tier first
                        price = 0.0
                        for god_card, god_price in GOD_TIER_CARDS.items():
                            if god_card.lower() in name.lower() and "base" in set_code:
                                price = god_price
                                break
                            if god_card.lower() in name.lower() and "VMAX" in name and "Umbreon" in name:
                                price = god_price # Moonbreon Check
                                break
                        
                        # If not God Tier, use Rarity Engine
                        if price == 0.0:
                            # Default to Common price if rarity is unknown
                            low, high = PRICE_MAP.get(rarity, (0.25, 1.00))
                            price = round(random.uniform(low, high), 2)

                        # 3. SAVE
                        p = Product(
                            game='PKM',
                            name=name,
                            price=price,
                            stock_count=random.randint(5, 20),
                            description=f"Set: {set_code.upper()} | Rarity: {rarity}",
                            image_url=image_url
                        )
                        batch.append(p)
                    
                    except Exception:
                        continue

                if batch:
                    Product.objects.bulk_create(batch)
                    self.stdout.write(f"Success! Imported {len(batch)} cards from {set_code}.")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))

        self.stdout.write("Starting GitHub Import...")
        for s in TARGET_SETS:
            fetch_set_from_github(s)
            
        self.stdout.write(self.style.SUCCESS("Done! You now have ALL the data with 0 API calls."))