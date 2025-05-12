import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from button_lock.models import State
from django.views.decorators.http import require_POST
from lesson.models import ChatRoom
from IDE.models import Course


def revise_button(request,group_id,data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何根据状态值禁用按钮", and
    adapt the framework but modify the detailed logic.
    '''
    if request.method == 'POST':
        course = Course.objects.get(slug=data_course)
        room = ChatRoom.objects.get(name=group_id, course=course)
        button_state, created = State.objects.get_or_create(room_id=room.id)
        if request.user.is_authenticated:
            button_state.is_locked = True
            button_state.last_user = request.user.username
            button_state.save()
        return JsonResponse({'username': request.user.username})
    else:
        return HttpResponse("This is the group learn page")


def save_button(request,group_id,data_course):
    '''
    AI-generated-content
    tool: DeepSeek
    version: latest
    usage: I use the prompt "如何根据状态值禁用按钮", and
    adapt the framework but modify the detailed logic.
    '''
    if request.method == 'POST':
        course = Course.objects.get(slug=data_course)
        room = ChatRoom.objects.get(name=group_id, course=course)
        button_state, created = State.objects.get_or_create(room_id=room.id)

        # 新增代码保存逻辑
        request_data = json.loads(request.body)
        new_code = request_data.get('code', '')

        if request.user.is_authenticated:
            button_state.is_locked = False
            button_state.code = new_code  # 保存新代码
            button_state.save()
        return JsonResponse({'username': request.user.username,
                             'code': new_code,})
    else:
        return HttpResponse("This is the group learn page")

def get_button_state(request,group_id,data_course):
    '''
    AI-generated-content
    tool: DeepSeek
    version: latest
    usage: I use the prompt "如何根据状态值禁用按钮", and
    adapt the framework but modify the detailed logic.
    '''
    course = Course.objects.get(slug=data_course)
    room = ChatRoom.objects.get(name=group_id, course=course)
    button_state, created = State.objects.get_or_create(room_id=room.id)
    return JsonResponse({'is_locked': button_state.is_locked, 'last_user':button_state.last_user,
                         'username': request.user.username,'code': button_state.code })