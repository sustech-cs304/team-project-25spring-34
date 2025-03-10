from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def index(request):
    return render(request, 'register.html')

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('IDE/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
