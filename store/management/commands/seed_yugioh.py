from django.core.management.base import BaseCommand
from store.models import Product
import requests

class Command(BaseCommand):
    help = "Populate the database with Yu-Gi-Oh! cards"

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old Yu-Gi-Oh! data...")
        Product.objects.filter(game='YGO').delete()

        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        
        self.stdout.write("Fetching cards...")
        
        try:
            response = requests.get(url)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Error connecting: {response.status_code}"))
                return

            data = response.json()
            cards = data.get("data", [])
            count = 0
            
            batch = []

            for card in cards:
                try:
                    if "card_prices" in card and "card_images" in card:
                        
                        price = float(card["card_prices"][0].get("tcgplayer_price", 0.00))
                        image = card["card_images"][0].get("image_url", "")

                        if price > 0 and image:
                            p = Product(
                                game="YGO",
                                name=card["name"],
                                price=price,
                                stock_count=5,
                                description=card.get("desc", "No description."),
                                image_url=image
                            )
                            batch.append(p)
                            count += 1
                        
                        if len(batch) >= 1000:
                            Product.objects.bulk_create(batch)
                            self.stdout.write(f"Saved {count} cards...")
                            batch = []

                except Exception as e:
                    self.stdout.write(f"Skipped {card.get('name', 'unknown')}: {e}")

            if batch:
                Product.objects.bulk_create(batch)

            self.stdout.write(self.style.SUCCESS(f"Import complete! Total cards imported: {count}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical Error: {e}"))
    