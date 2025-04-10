from django.shortcuts import render, redirect
from django.shortcuts import reverse
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib.auth.models import User
from group_learn.models import ButtonState
from django.http import JsonResponse


def index(request, group_id):
    return render(request, 'group-learn.html', {'group_id': group_id})

def room(request, group_id):
    print(request.user)
    if not request.user.is_authenticated:
        # return redirect(reverse("chat:login"))
        return redirect(reverse("login"))
    if group_id:
        return render(request, "group-learn.html", {"group_id": group_id})
    else:
        return render(request, "group-learn.html", {"group_id": 0})
    
def revise_button(request):
    if request.method == 'POST':
        button_state, created = ButtonState.objects.get_or_create(id=1)
        if request.user.is_authenticated:
            button_state.is_locked = True
            button_state.last_user = request.user.username
            button_state.save()
        return JsonResponse({'username': request.user.username})

def save_button(request):
    if request.method == 'POST':
        button_state, created = ButtonState.objects.get_or_create(id=1)
        if request.user.is_authenticated:
            button_state.is_locked = False
            button_state.save()
        return JsonResponse({'username': request.user.username})
    
def get_button_state(request):
    button_state, created = ButtonState.objects.get_or_create(id=1)
    return JsonResponse({'is_locked': button_state.is_locked, 'last_user':button_state.last_user, 'username': request.user.username})
