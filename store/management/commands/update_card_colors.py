import time
import requests
from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Fetches color data from Scryfall for all MTG cards'

    def handle(self, *args, **kwargs):
        cards = Product.objects.filter(game='MTG')
        
        print(f"Found {cards.count()} cards to update...")

        for card in cards:
            url = f"https://api.scryfall.com/cards/named?exact={card.name}"
            
            try:
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    scryfall_colors = data.get('colors', [])

                    # 3. MAPPING LOGIC
                    if len(scryfall_colors) == 0:
                        new_color = 'C' # Colorless
                    elif len(scryfall_colors) > 1:
                        new_color = 'M' # Multicolored
                    else:
                        new_color = scryfall_colors[0] # Single color (W, U, B, R, G)

                    # 4. Save to Database
                    card.color = new_color
                    card.save()
                    print(f"Updated: {card.name} -> {new_color}")

                else:
                    print(f"Skipped: {card.name} (Not found on Scryfall)")
                
                # IMPORTANT: Sleep 100ms to be nice to Scryfall's API
                time.sleep(0.1)

            except Exception as e:
                print(f"Error updating {card.name}: {e}")

        print("Done! All colors updated.")