from django.urls import path
from . import views

app_name = 'IDE'

urlpatterns = [
    path('courses/', views.get_courses, name='get_courses'),
    path('add/', views.add_course, name='add_course'),
    path('delete/', views.delete_course, name='delete_course'),
]