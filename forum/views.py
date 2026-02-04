from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Comment
from .forms import TopicForm, CommentForm

# 1. THE LOBBY VIEW
def forum_home(request):
    game_code = request.GET.get('game', 'MTG') # Default to Magic
    topics = Topic.objects.filter(game_category=game_code).order_by('-created_at')

    context = {
        'topics': topics,
        'current_game': game_code
    }
    # Loads the file we just made above
    return render(request, 'forums.html', context)

# 2. THE THREAD VIEW
def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    
    # Handle Reply Logic
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.topic = topic
            comment.author = request.user
            comment.save()
            return redirect('topic_detail', pk=pk)
    else:
        form = CommentForm()

    context = {
        'topic': topic,
        'current_game': topic.game_category,
        'comment_form': form
    }
    # Loads the thread detail page we made earlier
    return render(request, 'forum_post.html', context)

# 3. CREATE TOPIC VIEW
@login_required(login_url='login')
def create_topic(request):
    game_code = request.GET.get('game', 'MTG')
    
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.game_category = game_code
            topic.save()
            # Send them back to the Lobby for that game
            return redirect(f'/forum/?game={game_code}')
    else:
        form = TopicForm()
    
    context = {
        'form': form, 
        'current_game': game_code
    }
    return render(request, 'create_topic.html', context)