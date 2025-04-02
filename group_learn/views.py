from django.shortcuts import render, redirect
from django.shortcuts import reverse
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib.auth.models import User

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
