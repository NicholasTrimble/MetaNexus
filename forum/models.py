from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):

    GAME_CHOICES = [
        ('MTG', 'Magic: The Gathering'),
        ('PKM', 'Pokemon'),
        ('YGO', 'Yu-Gi-Oh!'),
        ('GEN', 'General Discussion'),
    ]

    title = models.CharField(max_length=200)
    game_category = models.CharField(max_length=3, choices=GAME_CHOICES, default='GEN')
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    topic = models.ForeignKey(Topic, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.topic.title}"
    

