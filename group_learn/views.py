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

def index(request, group_id):
    if not request.user.is_authenticated:
        logger.warning("用户未登录，重定向到登录页面")
        return redirect(reverse("login"))
    try:
        room = ChatRoom.objects.get(id=group_id)
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
            "code": ""  # 提供默认值，防止模板渲染错误
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
def get_annotations(request, group_id):
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
def get_room_pdfs(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        pdf_files = RoomFile.objects.filter(room=room, file_name__iendswith='.pdf').select_related('room')

        pdf_list = [
            {
                'id': pdf.id,
                'file_name': pdf.file_name,
                'file_url': request.build_absolute_uri(
                    f"/login/IDE/lesson/group-{group_id}/group-learn/serve_pdf/{pdf.id}/"
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
def get_pdf(request, group_id, pdf_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        pdf_file = RoomFile.objects.get(id=pdf_id, room=room)
        if request.user != room.creator:
            return JsonResponse({
                'success': False,
                'error': '只有房间创建者可以获取 PDF 文件'
            }, status=403)

        return JsonResponse({
            'success': True,
            'file_name': pdf_file.file_name,
            'file_url': request.build_absolute_uri(
                f"/login/IDE/lesson/group-{group_id}/group-learn/serve_pdf/{pdf_file.id}/"
            ),
            'uploaded_at': pdf_file.uploaded_at.strftime('%Y-%m-%d %H:%M')
        })
    except RoomFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'PDF 文件不存在'}, status=404)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': '房间不存在'}, status=404)
    except Exception as e:
        logger.error(f"获取 PDF 文件失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_current_pdf(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        cache_key = f"current_pdf_{group_id}"
        pdf_data = django_cache.get(cache_key)

        if pdf_data:
            pdf_id = pdf_data.get('pdf_id')
            pdf_file = RoomFile.objects.get(id=pdf_id, room=room)
            return JsonResponse({
                'success': True,
                'pdf': {
                    'id': pdf_file.id,
                    'file_name': pdf_file.file_name,
                    'file_url': request.build_absolute_uri(
                        f"/login/IDE/lesson/group-{group_id}/group-learn/serve_pdf/{pdf_file.id}/"
                    ),
                    'uploaded_at': pdf_file.uploaded_at.strftime('%Y-%m-%d %H:%M')
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'pdf': None
            })
    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': '房间不存在'}, status=404)
    except RoomFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'PDF 文件不存在'}, status=404)
    except Exception as e:
        logger.error(f"获取当前 PDF 失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def set_current_pdf(request, group_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        if request.user != room.creator:
            return JsonResponse({
                'success': False,
                'error': '只有房间创建者可以设置 PDF'
            }, status=403)

        data = json.loads(request.body)
        pdf_id = data.get('pdf_id')
        if not pdf_id:
            return JsonResponse({
                'success': False,
                'error': '未提供 PDF ID'
            }, status=400)

        pdf_file = RoomFile.objects.get(id=pdf_id, room=room)
        cache_key = f"current_pdf_{group_id}"
        try:
            django_cache.set(cache_key, {
                'pdf_id': pdf_file.id,
                'file_name': pdf_file.file_name
            }, timeout=3600)
            logger.info(f"成功设置缓存: {cache_key}, PDF ID: {pdf_file.id}")
        except Exception as cache_error:
            logger.error(f"缓存设置失败: {str(cache_error)}")
            return JsonResponse({
                'success': False,
                'error': '无法保存 PDF 选择，请稍后重试'
            }, status=500)

        return JsonResponse({
            'success': True,
            'pdf': {
                'id': pdf_file.id,
                'file_name': pdf_file.file_name,
                'file_url': request.build_absolute_uri(
                    f"/login/IDE/lesson/group-{group_id}/group-learn/serve_pdf/{pdf_file.id}/"
                ),
                'uploaded_at': pdf_file.uploaded_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': '房间不存在'}, status=404)
    except RoomFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'PDF 文件不存在'}, status=404)
    except Exception as e:
        logger.error(f"设置当前 PDF 失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def serve_pdf(request, group_id, pdf_id):
    try:
        room = ChatRoom.objects.get(id=group_id)
        pdf_file = RoomFile.objects.get(id=pdf_id, room=room)

        def file_iterator(data, chunk_size=8192):
            for i in range(0, len(data), chunk_size):
                yield data[i:i + chunk_size]

        response = StreamingHttpResponse(
            file_iterator(pdf_file.file_data),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'inline; filename="{pdf_file.file_name}"'
        response['Content-Length'] = len(pdf_file.file_data)
        return response
    except RoomFile.DoesNotExist:
        logger.error(f"PDF 文件 {pdf_id} 不存在")
        return HttpResponse(status=404)
    except ChatRoom.DoesNotExist:
        logger.error(f"房间 {group_id} 不存在")
        return HttpResponse(status=404)
    except Exception as e:
        logger.error(f"提供 PDF 文件失败: {str(e)}")
        return HttpResponse(status=500)
