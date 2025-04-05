import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from lesson.models import ChatRoom, ChatMessage

# group_topics = dict()
# 使用Django缓存代替内存字典
TOPIC_CACHE_PREFIX = "chat_room_topic_"


def index(request, group_id):
    return render(request, 'group-id.html', {'group_id': group_id})

def group_id(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        return redirect(f'/login/IDE/lesson/group-{group_id}')
    return render(request, 'group-id.html')


@login_required
@csrf_exempt
def get_members(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
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
            'room_name': room.name
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '房间不存在'
        }, status=404)


@login_required
@require_POST
@csrf_exempt
def leave_room(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
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
def get_learning_topics(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
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
            'room_name': room.name
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

def validate_room(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
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
            'topics': topics
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'is_valid': False,
            'message': '房间不存在'
        }, status=404)


@login_required
@require_POST
@csrf_exempt
def update_topic(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
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
def upload_file(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        if request.user not in room.members.all():
            return JsonResponse({'status': 'error', 'message': '无权上传文件'}, status=403)

        if request.method == 'POST' and request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            room_file = RoomFile.objects.create(
                room=room,
                file=uploaded_file,
                uploaded_by=request.user
            )
            return JsonResponse({
                'status': 'success',
                'message': '文件上传成功',
                'file': {
                    'name': room_file.file.name,
                    'url': room_file.file.url,
                    'uploaded_at': room_file.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'uploaded_by': room_file.uploaded_by.username
                }
            })
        return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)
    
@login_required
def get_files(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        if request.user not in room.members.all():
            return JsonResponse({'status': 'error', 'message': '无权访问文件'}, status=403)

        files = room.files.all()
        file_list = [{
            'name': f.file.name,
            'url': f.file.url,
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
def delete_file(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        if request.user not in room.members.all():
            return JsonResponse({'status': 'error', 'message': '无权删除文件'}, status=403)

        if request.method == 'POST':
            data = json.loads(request.body)
            file_name = data.get('file_name')

            # 查找文件
            room_file = RoomFile.objects.filter(room=room, file=f'{file_name}').first()     
            if not room_file:
                return JsonResponse({'status': 'error', 'message': '文件不存在'}, status=404)

            # 删除文件
            file_path = os.path.join(settings.MEDIA_ROOT, room_file.file.name)
            if os.path.exists(file_path):
                os.remove(file_path)
            room_file.delete()

            return JsonResponse({'status': 'success', 'message': '文件已删除'})
        return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在'}, status=404)