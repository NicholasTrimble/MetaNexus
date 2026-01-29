from django.core.management.base import BaseCommand
from store.models import Product
import requests
import time
import random

class Command(BaseCommand):
    help = 'Populate the database with ALL Pokemon cards'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old Pokemon data...")
        Product.objects.filter(game='PKM').delete()

        page = 1
        has_more_cards = True
        
        while has_more_cards:
            self.stdout.write(f"Fetching page {page}...")

            url = f"https://api.pokemontcg.io/v2/cards?pageSize=250&page={page}"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 429:
                    self.stdout.write("Rate limit hit. Waiting 10 seconds...")
                    time.sleep(10)
                    continue
                
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f'Error: {response.status_code}'))
                    break

                data = response.json()
                cards = data.get('data', [])

                if not cards:
                    has_more_cards = False
                    break

                for card in cards:
                    try:
                        price = 0.0
                        if 'tcgplayer' in card and 'prices' in card['tcgplayer']:
                            prices = card['tcgplayer']['prices']
                            first_type = list(prices.keys())[0]
                            price = prices[first_type].get('market', 0.0) or prices[first_type].get('mid', 0.0)

                        if price > 0 and 'images' in card:
                            Product.objects.create(
                                game='PKM',
                                name=card['name'],
                                price=price,
                                stock_count=random.randint(1, 10),
                                description=f"Set: {card['set']['name']}", 
                                image_url=card['images']['large']
                            )
                    except Exception as e:
                        continue
                
                page += 1
                time.sleep(0.5)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Critical Error: {e}'))
                break

        self.stdout.write(self.style.SUCCESS(f'Done! Processed {page} pages.'))