from django.urls import path
from . import views

app_name = 'group_learn'

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path("save_annotations/", views.save_annotations, name="save_annotations"),
    path("get_annotations/", views.get_annotations, name="get_annotations"),
]
