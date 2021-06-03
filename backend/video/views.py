from django.shortcuts import render
import uuid

# Create your views here.
def index(request):
    return render(request, 'video/index.html')

def room(request, room_name):
    return render(request, 'video/room.html', {
        'room_name': room_name,
        'uuid': str(uuid.uuid4())
    })