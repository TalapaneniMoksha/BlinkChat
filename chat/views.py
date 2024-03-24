from django.shortcuts import render , redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from.models import Message, Room, Topic
from .forms import RoomForm,UserForm
from django.db.models import Max
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm
from .forms import MessageForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count
from django.contrib.auth.models import User
from .models import Room, Message
from datetime import datetime
# from django.contrib.auth.models import UserLogEntry  # Replace this with your actual login tracking model






def starting_page(request):
    return render(request,'chat/home1.html')
def second_page(request):
    return render(request,'chat/second.html')
def swami(request):
    return render(request,'chat/swami.html')






def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')

            form.save()
            user = authenticate(username=username, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully. You are now logged in.')
                return redirect('home')
        else:
            messages.error(request, 'Account creation failed. Please try again.')
            return redirect('register')
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
        try:
            user = User.objects.get(username=username)
            print(user)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'chat/login.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return render(request, 'chat/login.html')
    context ={'page':page}
    return render(request, 'chat/login.html',context)




def logoutUser(request):
    logout(request)
    return redirect('starting_page')




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
    print(request.FILES, 'this is in the view')
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.room = room
            message.save()
            room.participants.add(request.user)
            return redirect('room', pk=room.id)
    else:
        form = MessageForm()

    context = {'room': room, 'room_messages': room_messages, 'participants': participants, 'form': form}
    return render(request, 'chat/room.html', context)



def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages,'topics':topics}
    return render(request, 'chat/profile.html',context)




@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if not request.user.is_superuser:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        restricted = request.POST.get('restricted') == 'on'  # Check if room is restricted

        room = Room.objects.create(   #  room creation
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            restricted=restricted  
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
def delete_user(request):
    if request.method == 'POST' and request.user == request.user:
        request.user.delete()
        logout(request)
        return redirect('home')  # Redirect to your desired page after deletion
    elif request.method == 'POST':
        return HttpResponseForbidden("You don't have permission to delete this account.")
    return render(request, 'chat/delete_user.html')
 
def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        default_password = 'omsrisairam'  # Set your default password here

        try:
            user = User.objects.get(username=username)
            user.set_password(default_password)
            user.save()
            messages.success(request, f"Password reset for {username} successful. New password: {default_password}")
            return redirect('home')  # Redirect to the 'home' page
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, 'chat/reset_password.html')



def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'chat/change_password.html', {'form': form})


# In your views.py



def user_statistics(request, user_id):
    user = User.objects.get(id=user_id)
    
    # Last login date and time
    last_login = user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "Never"

    # Total number of messages sent by the user
    total_messages_sent = user.message_set.count()

    # Total number of rooms joined by the user
    total_rooms_joined = user.room_set.count()
    
    # total_logins = UserLogEntry.objects.filter(user=user).count()  # Replace UserLogEntry with your actual login tracking model
    
    # Total number of rooms created by the user
    total_rooms_created = Room.objects.filter(host=user).count()

    # Most active rooms (rooms where the user sent the most messages)
    most_active_rooms = user.room_set.annotate(message_count=Count('message')).order_by('-message_count')[:5]

    context = {
        'user': user,
        'last_login': last_login,
        'total_messages_sent': total_messages_sent,
        'total_rooms_joined': total_rooms_joined,
        'total_rooms_created': total_rooms_created,
        'most_active_rooms': most_active_rooms,
        # 'total_logins': total_logins,
    }
    print(context)
    return render(request, 'chat/user_statistics.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from .models import Room

@login_required(login_url='login')
def unsubscribe_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room.participants.remove(request.user)
        return redirect('home')  # Redirect to home or any appropriate page after unsubscribing
    return render(request, 'chat/unsubscribe_room.html', {'room': room})


login_required
def admin_inter(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            user.is_superuser = True
            user.save()
            messages.success(request, f"{username} has been promoted to superuser.")
            return redirect('home')  # Redirect to admin dashboard or any other page
        except User.DoesNotExist:
            messages.error(request, f"User with username {username} does not exist.")
            return redirect('admin_inter')


    return render(request,'chat/grant_to_admin.html')
