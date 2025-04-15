from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    return render(request, 'IDE.html')

def user_login(request):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何实现用户登录", and
    directly use the method.
    '''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('IDE/') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
