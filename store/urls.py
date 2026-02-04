from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.store, name='store'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='store'), name='logout'),
    path('add-card-to-deck/', views.add_card_to_deck, name='add_card_to_deck'),
    path('decks/', views.deck_list, name='deck_list'),
    path('decks/create/', views.create_deck, name='create_deck'),
    path('decks/delete/<int:deck_id>/', views.delete_deck, name='delete_deck'),
    path('decks/<int:deck_id>/', views.deck_detail, name='deck_detail'),
    path('decks/<int:deck_id>/remove/<int:card_id>/', views.remove_from_deck, name='remove_from_deck'),
    path('api/search/', views.search_api, name='api_search'),
]

