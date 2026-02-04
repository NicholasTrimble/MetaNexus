from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Deck, DeckCard 
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def store(request):
    game_type = request.GET.get('game', 'MTG')
    products = Product.objects.filter(game=game_type)
    user_decks = []
    if request.user.is_authenticated:
        user_decks = Deck.objects.filter(user=request.user)
    
    # Filter by Color
    selected_color = request.GET.get('color')
    if selected_color:
        products = products.filter(color=selected_color)

    # Filter by Type
    selected_type = request.GET.get('type')
    if selected_type:
        products = products.filter(card_type__icontains=selected_type)

    # Search Query
    query = request.GET.get('q') 
    if query:
        products = products.filter(name__icontains=query)

    sort_command = request.GET.get('sort')
    if sort_command == 'price_asc':
        products = products.order_by('price')
    elif sort_command == 'price_desc':
        products = products.order_by('-price')
    elif sort_command == 'newest':
        products = products.order_by('-id')
    else:
        products = products.order_by('name') 

    # Pagination
    paginator = Paginator(products, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the template with context
    context = {
        'products': page_obj, 
        'current_game': game_type,
        'user_decks': user_decks,
        'current_color': selected_color,
    }
    return render(request, 'store.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'register.html', context)


@login_required(login_url='login')
def deck_list(request):
    user_decks = Deck.objects.filter(user=request.user)
    context = {'decks': user_decks}
    return render(request, 'decks.html', context)

@login_required(login_url='login')
def create_deck(request):
    if request.method == 'POST':
        deck_name = request.POST.get('name', 'New Deck')
        game_type = request.POST.get('game_type', 'MTG')
        Deck.objects.create(user=request.user, name=deck_name, game=game_type)
        return redirect('deck_list')
    return render(request, 'decks.html')

@login_required(login_url='login')
def delete_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    deck.delete()
    return redirect('deck_list')



@login_required(login_url='login')
def add_card_to_deck(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        deck_id = data.get('deck_id')
        
        if deck_id:
            deck = Deck.objects.filter(id=deck_id, user=request.user).first()
        else:
            deck = Deck.objects.filter(user=request.user).order_by('-created_at').first()
        
        if not deck:
            return JsonResponse({'status': 'error', 'message': 'Create a deck first!'})

        product = get_object_or_404(Product, id=product_id)
        
        deck_card, created = DeckCard.objects.get_or_create(
            deck=deck,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            deck_card.quantity += 1
            deck_card.save()
            
        return JsonResponse({
            'status': 'success', 
            'message': f"Added {product.name} to {deck.name}!"
        })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@login_required(login_url='login')
def deck_detail(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    
    deck_cards = deck.cards.all().select_related('product')
    
    context = {
        'deck': deck,
        'deck_cards': deck_cards
    }
    return render(request, 'deck_detail.html', context)

@login_required(login_url='login')
def remove_from_deck(request, deck_id, card_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    
    deck_card = get_object_or_404(DeckCard, deck=deck, product_id=card_id)
    
    if deck_card.quantity > 1:
        deck_card.quantity -= 1
        deck_card.save()
    else:
        deck_card.delete()
        
    return redirect('deck_detail', deck_id=deck.id)


def search_api(request):
    query = request.GET.get('q', '')
    game_type = request.GET.get('game', 'MTG')
    products = Product.objects.filter(game=game_type, name__icontains=query)[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image_url': product.image_url
        })
    
    return JsonResponse({'results': results})