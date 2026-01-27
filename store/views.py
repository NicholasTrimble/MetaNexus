from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


def store(request):
    products = Product.objects.all()
    sort_command = request.GET.get('sort') 
    
    if sort_command == 'price_asc':
        products = products.order_by('price')
    elif sort_command == 'price_desc':
        products = products.order_by('-price')
    elif sort_command == 'newest':
        products = products.order_by('-id')  
        
    context = {'products': products}
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
