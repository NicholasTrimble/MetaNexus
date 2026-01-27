from django.shortcuts import render
from .models import Product, Order, OrderItem

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


