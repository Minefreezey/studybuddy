from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required 
from .models import Room, Topic, Message
from django.contrib.auth.models import User
from .forms import RoomForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

# rooms = [
#     {'id': 1,'name': 'Lets learn python!'},
#     {'id': 2,'name': 'Design with me'},
#     {'id': 3,'name': 'Frontend developer'},
# ]
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, 'User does not exist!')

        user = authenticate(request, username = username, password= password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username or Password does not correct!')

    contex = {'page':page}
    return render(request, 'base/login_register.html',contex)

def logoutUser(request):
    logout(request) # this will delete session token, and therefore deleting that user's session
    return redirect('home')

def registerUser(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # commit is false is to we can be able to access the user, such as editing 
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    return render(request, 'base/login_register.html',{'form':form})

def home(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) | 
        Q(name__icontains = q) |
        Q(description__icontains = q )
        ) #this filter the query contains what is in q

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.all() # this can filter to condition (eg. your friends)
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains = q)
    )

    contex = {'rooms' : rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',contex)

def room(request,pk):
    room = Room.objects.get(id=pk) # search the base by condition that id must be pk variable
    room_messages = room.message_set.all().order_by('-created') # message is the child object of specific room, it's mean giving the set of all message that there related to this specific room
    participants = room.participants.all() # .all() is used in many-to-many relationship
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'), # this is the name of the HTML input template <form name = "body">
                        
        )
        room.participants.add(request.user)
        return redirect ('room', pk = room.id)
    contex = {'room':room,'room_messages':room_messages, 'participants':participants}
    return render(request,'base/room.html',contex) # we want this page to reload completely to avoid messing with POST method

def userProfile(request,userID):
    user = User.objects.get(id = userID)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request, 'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False) # save it into database, (commit = False means that we are not save submitting)
            room.host = request.user
            room.save()
            return redirect('home') # the 'home' is the url's name attribute, not the link
    context = {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request, roomID):
    room = Room.objects.get(id = roomID)
    form = RoomForm(instance=room) #this form will be prefield with room field values
    
    if request.user != room.host and (request.user.is_superuser == False):
        return HttpResponse('You are not the room owner!')
    if request.method == "POST":
        form = RoomForm(request.POST,instance=room) #We need to tell which room to update, if no, it will just create a new room
        if form.is_valid():
            form.save()
            return redirect('home')
    contex = {'form': form}
    return render(request, 'base/room_form.html',contex)

@login_required(login_url='login')
def deleteRoom(request, roomID):
    room = Room.objects.get(id = roomID)
    if request.user != room.host and (request.user.is_superuser == False):
        return HttpResponse('You are not the room owner!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request, roomID):
    message = Message.objects.get(id = roomID)
    if request.user != message.user and (request.user.is_superuser == False):
        return HttpResponse('You do not create this message')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message}) #delete.html is dynamic page that can delete anything you sent
# Create your views here.
