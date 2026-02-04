from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('create/', views.create_topic, name='create_topic'),
]