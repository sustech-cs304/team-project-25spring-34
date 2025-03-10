from django.shortcuts import render

def index(request, group_id):
    return render(request, 'group-learn.html', {'group_id': group_id})
