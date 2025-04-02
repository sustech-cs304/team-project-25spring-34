from django.urls import path
from . import views

app_name = 'lesson'

urlpatterns = [
    path("", views.index, name="index"),
    path('create-room/', views.create_room, name='create_room'),
    path('join-room/', views.join_room, name='join_room'),
    path('delete-room/group-<str:room_name>/', views.delete_room, name='delete_room'),
]