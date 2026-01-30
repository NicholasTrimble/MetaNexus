from django.core.management.base import BaseCommand
from store.models import Product
import requests
import random
import time

class Command(BaseCommand):
    help = 'Imports the "Greatest Hits" Sets '

    def handle(self, *args, **kwargs):
        
        API_KEY = "tcg_92fb4c5b446341b3bbafea691cef4da0"


        self.stdout.write("Clearing old Pokemon data...")
        Product.objects.filter(game='PKM').delete()

        BASE_URL = "https://api.justtcg.com/v1"
        HEADERS = {"x-api-key": API_KEY}
        
        TARGET_SETS = [
            "Base Set",           
            "Scarlet & Violet 151", 
            "Evolving Skies",      
            "Crown Zenith"         
        ]

        def get_set_id(name):
            try:
                response = requests.get(f"{BASE_URL}/sets", headers=HEADERS, params={"game": "Pokemon"})
                response.raise_for_status()
                sets = response.json().get("data", [])
                for s in sets:
                    if name.lower() == s['name'].lower():
                        return s['id']
                    if name.lower() in s['name'].lower():
                        return s['id']
            except Exception:
                return None
            return None

        def fetch_set(set_name):
            set_id = get_set_id(set_name)
            if not set_id:
                self.stdout.write(self.style.ERROR(f"Could not find Set ID for {set_name}"))
                return

            self.stdout.write(f"\n--- Importing Set: {set_name} ---")
            
            url = f"{BASE_URL}/cards"
            limit = 20 
            offset = 0
            has_more = True

            while has_more:
                params = {
                    "set": set_id,
                    "limit": limit,
                    "offset": offset, 
                }
                
                try:
                    response = requests.get(url, headers=HEADERS, params=params)
                    if response.status_code == 429:
                        self.stdout.write(self.style.ERROR("Rate Limit Hit! Stopping for today."))
                        return 

                    response.raise_for_status()
                    data = response.json()
                    cards = data.get("data", [])
                    
                    if not cards:
                        has_more = False
                        break

                    batch = []
                    for card in cards:
                        try:
                            image_url = card.get('image')
                            
                            market_price = 0.0
                            variant_label = "Standard"
                            
                            if card.get("variants"):
                                best_variant = max(
                                    (v for v in card["variants"]), 
                                    key=lambda x: x.get("price", 0)
                                )
                                market_price = best_variant.get("price", 0.0)
                                variant_label = best_variant.get("printing", "Normal")
                                if not image_url:
                                    image_url = best_variant.get('image')

                            if market_price > 0 and image_url:
                                p = Product(
                                    game='PKM',
                                    name=card['name'],
                                    price=market_price,
                                    stock_count=random.randint(2, 5),
                                    description=f"Set: {set_name}. {variant_label}",
                                    image_url=image_url
                                )
                                batch.append(p)
                        except Exception:
                            continue

                    if batch:
                        Product.objects.bulk_create(batch)
                        self.stdout.write(f"Saved {len(batch)} cards... (Total saved: {Product.objects.count()})")

                    offset += limit
                    
                    time.sleep(7) 

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e}"))
                    has_more = False

        self.stdout.write("Starting 'Greatest Hits' Import...")
        
        for s in TARGET_SETS:
            fetch_set(s)
            
        self.stdout.write(self.style.SUCCESS("All Sets Imported Successfully!"))