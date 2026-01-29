from django.core.management.base import BaseCommand
from store.models import Product
import requests
import time

class Command(BaseCommand):
    help = 'Populates DB by downloading every Set file from GitHub'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old Pokemon data...")
        Product.objects.filter(game='PKM').delete()

        sets_url = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/sets/en.json"
        
        try:
            self.stdout.write("Fetching list of Sets...")
            response = requests.get(sets_url)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR("Could not find Set list."))
                return

            all_sets = response.json()
            self.stdout.write(f"Found {len(all_sets)} sets. Starting import...")

            total_cards = 0

            for set_data in all_sets:
                set_id = set_data['id']
                set_name = set_data['name']
                
                cards_url = f"https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/cards/en/{set_id}.json"
                
                try:
                    set_res = requests.get(cards_url)
                    if set_res.status_code != 200:
                        continue

                    cards = set_res.json()
                    
                    batch = []
                    
                    for card in cards:
                        if 'images' not in card:
                            continue

                        price = 0.00
                        if 'tcgplayer' in card and 'prices' in card['tcgplayer']:
                            prices = card['tcgplayer']['prices']
                            if prices:
                                first_type = list(prices.keys())[0]
                                price = prices[first_type].get('mid', 0.0) or prices[first_type].get('market', 0.0)
                        
                        if price == 0:
                            price = 5.00

                        p = Product(
                            game='PKM',
                            name=card['name'],
                            price=price,
                            stock_count=5,
                            description=f"Set: {set_name}. Rarity: {card.get('rarity', 'Common')}",
                            image_url=card['images']['small']
                        )
                        batch.append(p)
                        total_cards += 1

                    Product.objects.bulk_create(batch)
                    self.stdout.write(f"Imported {set_name} ({len(batch)} cards)")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {set_name}: {e}"))

            self.stdout.write(self.style.SUCCESS(f'GRAND TOTAL: Imported {total_cards} cards!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical Error: {e}"))