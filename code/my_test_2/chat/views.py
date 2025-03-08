from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage


def index(request):
    print(request.user)
    return render(request, "chat/index.html")

def room(request, room_name):
    print(request.user)
    if not request.user.is_authenticated:
        # print(reverse("chat:login"))
        # return redirect(reverse("chat:login"))
        return redirect(reverse("chat:login"))
    if room_name:
        return render(request, "chat/room.html", {"room_name": room_name})
    else:
        return render(request, "chat/room.html", {"room_name": 'public'})

def register(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            u = User.objects.create_user(username=username, password=password)
            user_login(request,u)
            return HttpResponse("注册成功")
        except Exception as e:
            print(e)
            return HttpResponse("注册失败， 请重试")

    if request.method == "GET":
        return render(request, 'chat/register.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username, password)
        u = authenticate(request, username=username, password=password)
        if u:
            user_login(request,u)
            return HttpResponse("登录成功")
        else:
            return HttpResponse("用户名或密码错误")

    if request.method == "GET":
        return render(request, 'chat/login.html')

def logout(request):
    user_logout(request)
    return render(request, 'chat/login.html')