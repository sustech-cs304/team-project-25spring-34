from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from app1.models import ButtonState
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

def index(request):
    button_state, created = ButtonState.objects.get_or_create(id=1)
    context = {
        'is_locked': button_state.is_locked,
        'username': request.user.username if request.user.is_authenticated else None
    }
    return render(request,'index.html', context)

def revise_button(request):
    if request.method == 'GET':
        button_state, created = ButtonState.objects.get_or_create(id=1)
        if request.user.is_authenticated:
            button_state.is_locked = True
            button_state.last_user = request.user.username
            button_state.save()
        return JsonResponse({'username': request.user.username})

def save_button(request):
    if request.method == 'GET':
        button_state, created = ButtonState.objects.get_or_create(id=1)
        if request.user.is_authenticated:
            button_state.is_locked = False
            button_state.save()
        return JsonResponse({'username': request.user.username})
    
def get_button_state(request):
    button_state, created = ButtonState.objects.get_or_create(id=1)
    return JsonResponse({'is_locked': button_state.is_locked, 'last_user':button_state.last_user, 'username': request.user.username})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index/') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

