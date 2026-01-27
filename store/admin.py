from django.contrib import admin
from .models import Product, Deck, DeckCard

# Register your models here.
admin.site.register(Product)
admin.site.register(Deck)
admin.site.register(DeckCard)