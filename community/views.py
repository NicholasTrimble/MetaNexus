from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def room(request, room_name):
    return render(request, 'chat_room.html', {
        'room_name': room_name
    })