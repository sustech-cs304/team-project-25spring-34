from django.urls import path
from . import views

urlpatterns = [
    path('get_button_state/', views.get_button_state, name='get_button_state'),
    path('save_button/', views.save_button, name='save_button'),
    path('revise_button/', views.revise_button, name='revise_button'),
]