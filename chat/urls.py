from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import unsubscribe_room


urlpatterns =[
         path('', views.starting_page, name="starting_page"),
         path('second_page/',views.second_page, name="second_page"),
         path('login/',views.loginPage,name="login"),
         path('logout/',views.logoutUser,name="logout"),
         path('register/',views.register,name="register"),
         path('room/<str:pk>/',views.room , name ="room"),
         path('profile/<str:pk>/',views.userProfile , name ="user-profile"),
         path('home/',views.home, name="home"),
         path('create-room/', views.createRoom, name="create-room"),
         path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
         path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
         path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
         path('update-user/', views.updateUser, name="update-user"),
         path('topics/', views.topicPage, name="topics"),
         path('change_password/', views.change_password, name='change_password'),
         path('delete_user/', views.delete_user, name="delete_user"),
         path('reset_password/', views.reset_password, name='reset_password'),
         path('user-statistics/<int:user_id>/', views.user_statistics, name='user_statistics'),
        path('admin_inter/',views.admin_inter, name="admin_inter"),

        #  path('unsubscribe-room/<int:room_id>/', views.unsubscribe_room, name='unsubscribe-room'),



        #  path('send_message/<int:room_id>/', views.send_message, name='send_message'),

         

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)