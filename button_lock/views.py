from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from button_lock.models import State
from django.views.decorators.http import require_POST

def revise_button(request,group_id):
    if request.method == 'POST':
        button_state, created = State.objects.get_or_create(id=group_id)
        if request.user.is_authenticated:
            button_state.is_locked = True
            button_state.last_user = request.user.username
            button_state.save()
        return JsonResponse({'username': request.user.username})
    else:
        return HttpResponse("This is the group learn page")

def save_button(request,group_id):
    if request.method == 'POST':
        button_state, created = State.objects.get_or_create(id=group_id)
        if request.user.is_authenticated:
            button_state.is_locked = False
            button_state.save()
        return JsonResponse({'username': request.user.username})
    else:
        return HttpResponse("This is the group learn page")

def get_button_state(request,group_id):
    button_state, created = State.objects.get_or_create(id=group_id)
    return JsonResponse({'is_locked': button_state.is_locked, 'last_user':button_state.last_user, 'username': request.user.username})
