from django.shortcuts import render, redirect

def index(request, group_id):
    return render(request, 'group-id.html', {'group_id': group_id})

def group_id(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        return redirect(f'/login/IDE/lesson/group-{group_id}')
    return render(request, 'group-id.html')
