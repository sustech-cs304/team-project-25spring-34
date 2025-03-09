"""
URL configuration for IDEframework project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path
from login import views as login_views
from register import views as register_views
from lock_button import views as lock_button_views
from IDE import views as IDE_views
from lesson import views as lesson_views

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/IDE/', login_views.index),
    path('register/IDE/', register_views.index),
    path('login/IDE/lesson', IDE_views.index),
    path('register/IDE/lesson/self-learn', lesson_views.index),
    path('login/IDE/lesson/self-learn', lesson_views.index),
    path('register/IDE/lesson/', lesson_views.index),
    # path('revise_button/', lock_button_views.revise_button, name='revise_button'),
    # path('save_button/', lock_button_views.save_button, name='save_button'),
    # path('get_button_state/', lock_button_views.get_button_state, name='get_button_state'),
    path('login/', login_views.user_login, name='login'),
    path('register/', register_views.user_register, name='register'),
]
