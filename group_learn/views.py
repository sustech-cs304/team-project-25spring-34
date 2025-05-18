from linecache import cache
from venv import logger

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import reverse
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache as django_cache
from .models import Annotation
from django.views.decorators.csrf import csrf_exempt
import json
from group_id.models import RoomFile
from lesson.models import ChatRoom
import logging
# def index(request, group_id):
#     room = ChatRoom.objects.get(id=group_id)
#     is_creator = request.user == room.creator
#     return render(request, 'group-learn.html', {'group_id': group_id, "is_creator": is_creator})

logger = logging.getLogger(__name__)

def index(request, group_id, data_course):
    '''
    AI-generated-content 
    tool: DeepSeek 
    version: latest 
    usage: I use the prompt "如何显示信息", and
    adapt some codes but add extra details.
    '''
    if not request.user.is_authenticated:
        logger.warning("用户未登录，重定向到登录页面")
        return redirect(reverse("login"))
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        is_creator = request.user == room.creator
        pdf_files = RoomFile.objects.filter(room=room, file_name__iendswith='.pdf')

        logger.info(f"Group ID: {group_id}")
        logger.info(f"当前用户: {request.user.username} (ID: {request.user.id})")
        logger.info(f"房间创建者: {room.creator.username} (ID: {room.creator.id})")
        logger.info(f"is_creator: {is_creator}")

        return render(request, "group-learn.html", {
            "group_id": group_id,
            "room": room,
            "pdf_files": pdf_files,
            "is_creator": is_creator,
            "code": "",  # 提供默认值，防止模板渲染错误
            "data_course": data_course,
        })
    except ChatRoom.DoesNotExist:
        logger.error(f"房间 {group_id} 不存在")
        return render(request, "group-learn.html", {"group_id": 0})

@csrf_exempt
def save_annotations(request, group_id):
    """
    AI-generated-content
    tool: GitHub Copilot
    version: latest
    usage: I used Copilot to fix syntax errors and standardize code.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        pdf_url = data.get('pdf_url')
        annotations = data.get('annotations')

        if not (pdf_url and annotations):
            return JsonResponse({'error': 'Invalid data'}, status=400)

        # 删除旧记录，确保唯一性
        Annotation.objects.filter(group_id=group_id, pdf_url=pdf_url).delete()

        # 创建新记录
        annotation = Annotation.objects.create(
            group_id=group_id,
            pdf_url=pdf_url,
            data=annotations
        )
        return JsonResponse({'success': True, 'created': True})

@csrf_exempt
def get_annotations(request, group_id, data_course):
    """
    AI-generated-content
    tool: GitHub Copilot
    version: latest
    usage: I used Copilot to fix syntax errors and standardize code.
    """
    if request.method == 'GET':
        pdf_url = request.GET.get('pdf_url')

        if not pdf_url:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        try:
            annotation = Annotation.objects.get(group_id=group_id, pdf_url=pdf_url)
            return JsonResponse({'success': True, 'annotations': annotation.data})
        except Annotation.DoesNotExist:
            return JsonResponse({'success': True, 'annotations': {}})

# ========creator共享PDF=========
@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_room_pdfs(request, group_id, data_course):
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        pdf_files = RoomFile.objects.filter(room=room, file_name__iendswith='.pdf').select_related('room')

        pdf_list = [
            {
                'id': pdf.id,
                'file_name': pdf.file_name,
                'file_url': request.build_absolute_uri(
                    f"/login/IDE/{data_course}/group-{group_id}/group-learn/serve_pdf/{pdf.id}/"
                ),
                'uploaded_at': pdf.uploaded_at.strftime('%Y-%m-%d %H:%M')
            }
            for pdf in pdf_files
        ]

        return JsonResponse({
            'success': True,
            'pdfs': pdf_list
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': '房间不存在'}, status=404)
    except Exception as e:
        logger.error(f"获取 PDF 列表失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_pdf(request, group_id, pdf_id, data_course):
    """
    AI-generated-content
    tool: deepseek
    version: latest
    usage: I used deepseek to prompt json response and handle ‘build_absolute_uri’ and ‘日期时间格式化操作’.
    """
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        pdf_file = RoomFile.objects.get(id=pdf_id, room=room)
        if request.user != room.creator:
            return JsonResponse({
                'success': False,
                'error': '只有房间创建者可以获取PDF文件'
            }, status=403)

        return JsonResponse({
            'success': True,
            'file_name': pdf_file.file_name,
            'file_url': request.build_absolute_uri(
                f"/login/IDE/{data_course}/group-{group_id}/group-learn/serve_pdf/{pdf_file.id}/"
            ),
            'uploaded_at': pdf_file.uploaded_at.strftime('%Y-%m-%d %H:%M')
        })
    except RoomFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'PDF文件不存在'}, status=404)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': '房间不存在'}, status=404)
    except Exception as e:
        logger.error(f"获取 PDF 文件失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_current_pdf(request, group_id, data_course):
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        cache_key = f"current_pdf_{group_id}"
        pdf_id = django_cache.get(cache_key)

        if pdf_id:
            pdf_file = RoomFile.objects.get(id=pdf_id, room=room)
            return JsonResponse({
                'success': True,
                'pdf': {
                    'id': pdf_file.id,
                    'file_name': pdf_file.file_name,
                    'file_url': request.build_absolute_uri(
                        f"/login/IDE/{data_course}/group-{group_id}/group-learn/serve_pdf/{pdf_file.id}/"
                    ),
                    'uploaded_at': pdf_file.uploaded_at.strftime('%Y-%m-%d %H:%M')
                }
            })
        else:
            return JsonResponse({'success': True, 'pdf': None})

    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': '房间不存在'}, status=404)
    except RoomFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'PDF文件不存在'}, status=404)
    except Exception as e:
        logger.error(f"获取当前PDF失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def set_current_pdf(request, group_id, data_course):
    try:
        room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
        if request.user != room.creator:
            return JsonResponse({
                'success': False,
                'error': '只有房间创建者可以设置PDF'
            }, status=403)

        data = json.loads(request.body)
        pdf_id = data.get('pdf_id')
        if not pdf_id:
            return JsonResponse({'success': False, 'error': '未提供 PDF ID'}, status=400)

        # 验证 PDF 是否存在
        pdf_file = RoomFile.objects.get(id=pdf_id, room=room)

        # 只缓存 pdf_id，不存整个文件
        cache_key = f"current_pdf_{group_id}"
        django_cache.set(cache_key, pdf_id, timeout=86400)  # 缓存 24 小时

        return JsonResponse({
            'success': True,
            'pdf': {
                'id': pdf_file.id,
                'file_name': pdf_file.file_name,
                'file_url': request.build_absolute_uri(
                    f"/login/IDE/{data_course}/group-{group_id}/group-learn/serve_pdf/{pdf_file.id}/"
                ),
                'uploaded_at': pdf_file.uploaded_at.strftime('%Y-%m-%d %H:%M')
            }
        })

    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': '房间不存在'}, status=404)
    except RoomFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'PDF 文件不存在'}, status=404)
    except Exception as e:
        logger.error(f"设置当前PDF失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def serve_pdf(request, group_id, pdf_id, data_course):
    """
    AI-generated-content
    tool:deepseek
    version: latest
    usage: I used deepseek to generate how to use cache to get and store data.
    """
    cache_key = f"pdf_data_{group_id}_{pdf_id}"
    cached_data = django_cache.get(cache_key)

    if cached_data:
        # 从缓存获取文件数据
        file_data = cached_data['file_data']
        file_name = cached_data['file_name']
    else:
        try:
            # 查询数据库
            room = ChatRoom.objects.get(name=group_id, course__slug=data_course)
            pdf_file = RoomFile.objects.get(id=pdf_id, room=room)
            file_data = pdf_file.file_data
            file_name = pdf_file.file_name

            # 存入缓存（适合不经常修改的文件）
            django_cache.set(
                cache_key,
                {'file_data': file_data, 'file_name': file_name},
                timeout=3600  # 缓存1小时
            )
        except RoomFile.DoesNotExist:
            logger.error(f"PDF 文件 {pdf_id} 不存在")
            return HttpResponse(status=404)
        except ChatRoom.DoesNotExist:
            logger.error(f"房间 {group_id} 不存在")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"查询 PDF 文件失败: {str(e)}")
            return HttpResponse(status=500)

    # 返回 StreamingHttpResponse
    def file_iterator(data, chunk_size=8192):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    response = StreamingHttpResponse(
        file_iterator(file_data),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'inline; filename="{file_name}"'
    response['Content-Length'] = len(file_data)
    return response

