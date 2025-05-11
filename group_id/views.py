import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from lesson.models import ChatRoom, ChatMessage
from group_id.models import RoomFile, Task

# group_topics = dict()
# 使用Django缓存代替内存字典
TOPIC_CACHE_PREFIX = "chat_room_topic_"


def index(request, group_id, data_course):
    return render(request, 'group-id.html', {'group_id': group_id, 'data_course': data_course})

def group_id(request, data_course):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        return redirect(f'/login/IDE/lesson/group-{group_id}')
    return render(request, 'group-id.html')


@login_required
@csrf_exempt
def get_members(request, group_id, data_course):
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user not in room.members.all():
            return JsonResponse({
                'status': 'error',
                'message': '无权访问该房间'
            }, status=403)

        members_data = [{
            'username': member.username,
            'is_leader': member == room.creator
        } for member in room.members.all()]

        return JsonResponse({
            'status': 'success',
            'members': members_data,
            'room_name': room.name,
            'data_course': data_course
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '房间不存在'
        }, status=404)


@login_required
@require_POST
@csrf_exempt
def leave_room(request, group_id, data_course):
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user in room.members.all():
            room.members.remove(request.user)
            return JsonResponse({
                'status': 'success',
                'message': '已成功离开房间'
            })
        return JsonResponse({
            'status': 'error',
            'message': '您不是该房间成员'
        }, status=403)
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '房间不存在'
        }, status=404)

@login_required
@require_POST
@csrf_exempt
def get_learning_topics(request, group_id, data_course):
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user not in room.members.all():
            return JsonResponse({
                'status': 'error',
                'message': '无权访问该房间'
            }, status=403)

        return JsonResponse({
            'status': 'success',
            # 'topics': group_topics.get(group_id or "暂无主题"),
            'topics': cache.get(f"{TOPIC_CACHE_PREFIX}{group_id}", "暂无主题"),
            'is_leader': request.user == room.creator,
            'room_name': room.name,
            'data_course': data_course
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '房间不存在'
        }, status=404)


from django.core.cache import cache
import json


@login_required
@require_POST
@csrf_exempt
def validate_room(request, group_id, data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "验证用户是否有权限访问指定的聊天室", and
    adapt the corresponding html to fetch data and update regularly.
    '''
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user not in room.members.all():
            return JsonResponse({
                'is_valid': False,
                'message': '无权访问该房间'
            }, status=403)

        # 从缓存获取主题
        topics = cache.get(f"{TOPIC_CACHE_PREFIX}{group_id}", "暂无主题")

        return JsonResponse({
            'is_valid': True,
            'room_name': room.name,
            'group_id': room.id,
            'leader': request.user == room.creator,
            'topics': topics,
            'data_course': data_course
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'is_valid': False,
            'message': '房间不存在'
        }, status=404)


@login_required
@require_POST
@csrf_exempt
def update_topic(request, group_id, data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何根据用户输入数据更改后端相应数据", and
    adapt the corresponding html to fetch data and update regularly.
    '''
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user != room.creator:
            return JsonResponse({
                'status': 'error',
                'message': '只有创建者可以修改主题'
            }, status=403)

        data = json.loads(request.body)
        new_topic = data.get('topic', '').strip()

        if not new_topic:
            return JsonResponse({
                'status': 'error',
                'message': '主题不能为空'
            }, status=400)

        # 使用缓存存储主题（设置1天过期）
        cache.set(f"{TOPIC_CACHE_PREFIX}{group_id}", new_topic, 86400)

        return JsonResponse({
            'status': 'success',
            'message': '主题更新成功',
            'new_topic': new_topic
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '房间不存在'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': '无效的JSON数据'
        }, status=400)
    
from .models import RoomFile

@login_required
@csrf_exempt
def upload_file(request, group_id, data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何将文件全部存入数据库", and
    adapt the framework but add extra logic and improve sql search speed.
    '''
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user not in room.members.all():
            return JsonResponse({'status': 'error', 'message': '无权上传文件'}, status=403)

        if request.method == 'POST' and request.FILES.get('file'):
            uploaded_file = request.FILES['file']

            existing_file = RoomFile.objects.filter(
                room=room,
                file_name=uploaded_file.name
            ).first()

            if existing_file:
                return JsonResponse({
                    'status': 'error',
                    'message': f'文件 "{uploaded_file.name}" 已经存在，不能重复上传'
                }, status=400)
            
            room_file = RoomFile.objects.create(
                room=room,
                file_name=uploaded_file.name,
                file_data=uploaded_file.read(),  # 读取文件的二进制数据
                uploaded_by=request.user
            )
            return JsonResponse({
                'status': 'success',
                'message': '文件上传成功',
                'file': {
                    'name': room_file.file_name,
                    'uploaded_at': room_file.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'uploaded_by': room_file.uploaded_by.username
                }
            })
        return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)
    
@login_required
def get_files(request, group_id, data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何从数据库读取文件", and
    adapt the framework but add extra logic and improve sql search speed.
    '''
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user not in room.members.all():
            return JsonResponse({'status': 'error', 'message': '无权访问文件'}, status=403)

        files = room.files.all().select_related('uploaded_by').only(
            'file_name', 'uploaded_at', 'uploaded_by__username'
        )
        file_list = [{
            'name': f.file_name,
            'uploaded_at': f.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'uploaded_by': f.uploaded_by.username
        } for f in files]

        return JsonResponse({'status': 'success', 'files': file_list})
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)

import os
from django.conf import settings
@login_required
@csrf_exempt
def delete_file(request, group_id, data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何从数据库删除文件", and
    adapt the framework but add extra logic and improve sql search speed.
    '''
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user not in room.members.all():
            return JsonResponse({'status': 'error', 'message': '无权删除文件'}, status=403)

        if request.method == 'POST':
            data = json.loads(request.body)
            file_name = data.get('file_name')

            deleted_count, _ = RoomFile.objects.filter(room=room, file_name=file_name).delete()
            if deleted_count == 0:
                return JsonResponse({'status': 'error', 'message': '文件不存在'}, status=404)
            
            return JsonResponse({'status': 'success', 'message': '文件已删除'})
        return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)

from django.http import HttpResponse

@login_required
def download_file(request, group_id, file_name, data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何实现下载文件", and
    adapt the framework but add extra logic.
    '''
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user not in room.members.all():
            return JsonResponse({'status': 'error', 'message': '无权下载文件'}, status=403)

        room_file = get_object_or_404(RoomFile, room=room, file_name=file_name)
        response = HttpResponse(room_file.file_data, content_type='application/octet-stream')

        if file_name.lower().endswith('.pdf'):
            response['Content-Type'] = 'application/pdf'
        elif file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            response['Content-Type'] = 'image/jpeg'
        else:
            response['Content-Type'] = 'application/octet-stream'

        if not request.GET.get('preview', False):
            response['Content-Disposition'] = f'attachment; filename="{room_file.file_name}"'

        return response
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)
    
@login_required
def get_tasks(request, group_id, data_course):
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        tasks = room.tasks.all().order_by('-created_at')
        task_list = [{
            'id': task.id,
            'text': task.text,
            'completed': task.completed,
            'category': task.category
        } for task in tasks]
        return JsonResponse({'status': 'success', 'tasks': task_list})
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)

@csrf_exempt
@login_required
def add_task(request, group_id, data_course):
    if request.method == 'POST':
        try:
            room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
            data = json.loads(request.body)
            task_text = data.get('text', '').strip()
            category = data.get('category', 'normal')

            if not task_text:
                return JsonResponse({'status': 'error', 'message': '任务内容不能为空'}, status=400)

            task = Task.objects.create(room=room, text=task_text, category=category)
            return JsonResponse({'status': 'success', 'task_id': task.id})
        except ChatRoom.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
@csrf_exempt
@login_required
def toggle_task(request, group_id, data_course):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            task = Task.objects.get(id=task_id, room__name=group_id)
            task.completed = not task.completed
            task.save()
            return JsonResponse({'status': 'success'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '任务不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
@csrf_exempt
@login_required
def update_task(request, group_id, data_course):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            new_text = data.get('text', '').strip()
            new_category = data.get('category')

            if not new_text:
                return JsonResponse({'status': 'error', 'message': '任务内容不能为空'}, status=400)

            task = Task.objects.get(id=task_id, room__name=group_id)
            task.text = new_text
            task.category = new_category
            task.save()
            return JsonResponse({'status': 'success'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '任务不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
@csrf_exempt
@login_required
def delete_task(request, group_id, data_course):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            task = Task.objects.get(id=task_id, room__name=group_id)
            task.delete()
            return JsonResponse({'status': 'success'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '任务不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
