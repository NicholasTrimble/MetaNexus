import requests
from django.core.management.base import BaseCommand
from store.models import Product
from django.db import transaction

class Command(BaseCommand):
    help = 'Updates card colors using Scryfall Bulk Data (FAST)'

    def handle(self, *args, **kwargs):
        print("Step 1: Fetching Scryfall Bulk Data URL...")
        meta_response = requests.get("https://api.scryfall.com/bulk-data")
        bulk_data_info = meta_response.json()
        
        download_uri = None
        for item in bulk_data_info['data']:
            if item['type'] == 'oracle_cards':
                download_uri = item['download_uri']
                break
        
        if not download_uri:
            print("Error: Could not find bulk data URI.")
            return

        print("Step 2: Downloading card database (approx 100MB)...")
        response = requests.get(download_uri)
        scryfall_data = response.json() 
        
        print("Step 3: Building lookup table...")
        card_colors_map = { card['name']: card.get('colors', []) for card in scryfall_data }

        print(f"Step 4: Updating your {Product.objects.count()} cards...")
        
        products = Product.objects.filter(game='MTG')
        updated_count = 0
        
        batch = []
        for product in products:
            if product.name in card_colors_map:
                scryfall_colors = card_colors_map[product.name]
                
                if len(scryfall_colors) == 0:
                    new_color = 'C' 
                elif len(scryfall_colors) > 1:
                    new_color = 'M' 
                else:
                    new_color = scryfall_colors[0] 
                
                if product.color != new_color:
                    product.color = new_color
                    batch.append(product)
                    updated_count += 1
            
            if len(batch) >= 1000:
                Product.objects.bulk_update(batch, ['color'])
                print(f"Saved {updated_count} updates so far...")
                batch = []

        if batch:
            Product.objects.bulk_update(batch, ['color'])

        print(f"SUCCESS: Updated {updated_count} cards with color data!")