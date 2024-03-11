from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from.models import Message, Room, Topic
from .forms import RoomForm,UserForm
from django.db.models import Max
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm




# rooms = [
    
#     {'id':1 , 'name': 'lets learn python!'},
#     {'id':2 , 'name': 'lets learn java script!'},
#     {'id':3 , 'name': 'lets learn web development!'},
# ]

def starting_page(request):
    return render(request,'chat/home1.html')
def second_page(request):
    return render(request,'chat/second.html')


# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('home')  # Redirect to home page after registration
#     else:
#         form = UserCreationForm()
#     return render(request, 'chat/register.html', {'form': form})



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully. You are now logged in.')
                return redirect('login')
            else:
                messages.error(request, 'Account creation failed. Please try again.')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})



def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect ('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)
        # Check if the provided username exists in the database
        try:
            user = User.objects.get(username=username)
            print(user)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'chat/login.html')

        # Authenticate the user using the provided username and password
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # If authentication is successful, log in the user
            login(request, user)
            return redirect('home')
        else:
            # If authentication fails, display an error message
            messages.error(request, 'Invalid credentials. Please try again.')
            return render(request, 'chat/login.html')
    context ={'page':page}
    return render(request, 'chat/login.html',context)




def logoutUser(request):
    logout(request)
    return redirect('starting_page')


# def register(request):
#     page='register'
#     return render(request,'chat/register.html')


# def home(request):
#     q=request.GET.get('q') if request.GET.get('q') != None else ''
    
#     rooms = Room.objects.filter( 
#         Q(topic__name__icontains=q)|
#         Q(name__icontains = q)|
#         Q(description__icontains = q)
#         )
    
#     topics = Topic.objects.all()
#     room_count =rooms.count()
#     room_messages = Message.objects.all()
    
#     context = {'rooms':rooms,'topics':topics, 'room_count':room_count,room_messages:'room_messages'}
#     return render(request,'chat/home.html',context)


def home(request):
    q = request.GET.get('q', '') 
    # q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Simplified way to handle query parameter
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()

    # Retrieve recent messages related to the filtered rooms
    room_messages = Message.objects.filter(room__in=rooms).annotate(
        max_created=Max('created')
    ).order_by('-max_created')

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages
    }
    return render(request, 'chat/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages=room.message_set.all().order_by('-created')
    participants =room.participants.all()
    if request.method =='POST':
        room_message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
         )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
        
    
    context = {'room': room,'room_messages':room_messages,'participants':participants}
    return render (request,'chat/room.html',context)



def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages,'topics':topics}
    return render(request, 'chat/profile.html',context)



# @login_required(login_url='login')
# def createRoom(request):
#     form = RoomForm()
#     topics =Topic.objects.all()
#     if not request.user.is_superuser:
#         return HttpResponse('You are not allowed here!!')
    
#     if request.method == 'POST':
#         topic_name = request.POST.get('topic')
#         topic,created = Topic.objects.get_or_create(name=topic_name)
#         Room.objects.create(
#             host=request.user,
#             topic=topic,
#             name=request.POST.get('name'),
#             description=request.POST.get('description')
#         )
    
#         return redirect('home')
        
#     context ={'form': form, 'topics': topics}
#     return render(request,'chat/room_form.html',context)
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    # Check if the user is superuser
    if not request.user.is_superuser:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # Check if the room is restricted
        restricted = request.POST.get('restricted') == 'on'  # Convert checkbox value to boolean

        # Create the room
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            restricted=restricted  # Set the restricted field based on the checkbox value
        )

        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'chat/room_form.html', context)


@login_required(login_url='login')
def room_detail(request, room_id):
    room = Room.objects.get(id=room_id)

    # Check if the user is the host of the room or a superuser
    if request.user == room.host or request.user.is_superuser:
        user_can_type = True
    else:
        user_can_type = False

    context = {'room': room, 'user_can_type': user_can_type}
    return render(request, 'chat/room_detail.html', context)


# def send_message(request, room_id):
#     # Your message sending logic here
#     return HttpResponse("Message sent successfully")



@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics =Topic.objects.all()

    if request.user !=room.host:
        return HttpResponse('You are not allowed here!!')
    
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    
    context ={'form':form, 'topics': topics, 'room':room}
    return render(request,'chat/room_form.html',context)


@login_required(login_url='login')
def deleteRoom(request,pk):
    room =Room.objects.get(id=pk)
    
    if request.user !=room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method =='POST':
        room.delete()
        return redirect('home')
    return render(request, 'chat/delete.html',{'obj' :room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message =Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed to delete!!')
    
    if request.method =='POST':
        message.delete()
        return redirect('home')
    return render(request, 'chat/delete.html',{'obj' :message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
     form = UserForm(request.POST, instance=user)
     if form.is_valid():
        form.save()
        return redirect('user-profile', pk=user.id)
    
    
    return render (request , 'chat/update-user.html',{'form':form})


def topicPage(request):
    q = request.GET.get('q', '') 
    topics =Topic.objects.filter(name__icontains=q)
    return render(request,'chat/topics.html',{'topics':topics}) 



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to maintain the user's session
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user-profile', pk=request.user.pk)  # Redirect to profile with user's pk
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'chat/password.html', {
        'form': form
    })
