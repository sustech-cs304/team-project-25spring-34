from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def index(request):
    return render(request, 'register.html')

def user_register(request):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何实现用户注册", and
    directly use the method.
    '''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
