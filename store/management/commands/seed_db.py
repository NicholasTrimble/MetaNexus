from django.core.management.base import BaseCommand
from store.models import Product
import requests
import time

class Command(BaseCommand):
    help = 'Populate the database with cards'

    def handle(self, *args, **kwargs):
        
        
        self.stdout.write("Clearing old MTG data...")
        Product.objects.filter(game='MTG').delete()

        url = "https://api.scryfall.com/cards/search?q=game:paper&order=usd&dir=desc"
        
        count = 0
        
        
        while url:
            self.stdout.write(f"Fetching page... (Cards imported so far: {count})")
            
            
            response = requests.get(url)
            
           
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Error connecting: {response.status_code}'))
                break

            data = response.json()
            cards = data.get('data', [])

            
            for card in cards:
                try:
                    
                    if 'prices' in card and card['prices'].get('usd') and 'image_uris' in card:
                        
                        Product.objects.create(
                            game='MTG',
                            name=card['name'],
                            
                            price=float(card['prices']['usd']),
                            stock_count=5, 
                            description=card.get('oracle_text', 'No description.'),
                            image_url=card['image_uris']['normal']
                        )
                        count += 1
                        
                except Exception as e:
                    
                    print(f"Skipped {card.get('name', 'unknown')}: {e}")

            if data.get('has_more'):
                
                url = data.get('next_page')
                
                time.sleep(0.1)
            else:
                url = None

        self.stdout.write(self.style.SUCCESS(f'Done! Imported {count} cards.'))