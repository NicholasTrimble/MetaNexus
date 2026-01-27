from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Deck, DeckCard 
from django.core.paginator import Paginator

def store(request):
    game_type = request.GET.get('game', 'MTG')
    products = Product.objects.filter(game=game_type)
    
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

    paginator = Paginator(products, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj, 
        'current_game': game_type
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