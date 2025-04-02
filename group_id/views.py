import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from lesson.models import ChatRoom, ChatMessage

# group_topics = dict()

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

# 使用Django缓存代替内存字典
TOPIC_CACHE_PREFIX = "group_topic_"


@login_required
@require_POST
@csrf_exempt
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

