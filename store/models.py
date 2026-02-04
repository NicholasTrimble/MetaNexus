from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    GAME_CHOICES = [
        ('MTG', 'Magic: The Gathering'),
        ('PKM', 'Pokemon'),
        ('YGO', 'Yu-Gi-Oh!'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    game = models.CharField(max_length=3, choices=GAME_CHOICES, default='MTG') 
    stock_count = models.IntegerField()
    description = models.TextField()
    image_url = models.URLField(max_length=200)

    #filtering by color for MTG
    COLOR_CHOICES = [
        ('W', 'White'),
        ('U', 'Blue'),
        ('B', 'Black'),
        ('R', 'Red'),
        ('G', 'Green'),
        ('C', 'Colorless'),
        ('M', 'Multicolor'),
    ]
    color = models.CharField(max_length=1, choices=COLOR_CHOICES, blank=True, null=True)
    card_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=100, default="New Deck")
    game = models.CharField(max_length=3, choices=Product.GAME_CHOICES, default='MTG')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class DeckCard(models.Model):
    # I renamed related_name to 'cards' so you can do 'my_deck.cards.all()'
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.deck.name}"