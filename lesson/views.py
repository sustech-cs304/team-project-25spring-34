import os
#import fitz  # PyMuPDF
from urllib.parse import quote
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from IDE.models import Course


def index(request):
    return render(request, 'lesson.html')

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import ChatRoom


@login_required
def create_room(request, data_course):
    '''
        AI-generated-content
        tool: DeepSeek
        version: latest
        usage: I use the prompt "结合django数据库写法实现一个新房间的创建" and generate the corresponding json response.
    '''
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        course = Course.objects.get(slug=data_course)

        # 检查 name 和 course 组合是否已存在
        if ChatRoom.objects.filter(name=room_name, course=course).exists():
            return JsonResponse({
                'status': 'error',
                'message': f'课程 "{data_course}" 下已存在聊天室 "{room_name}"'
            }, status=400)

        # 创建新房间
        new_room = ChatRoom.objects.create(
            name=room_name,
            creator=request.user,
            course=course
        )

        # 添加创建者为成员
        new_room.members.add(request.user)

        return JsonResponse({
            'status': 'success',
            'room_id': new_room.name,
            'course': data_course,
            'message': '房间创建成功'
        })

    return redirect('index')


@login_required
def join_room(request, data_course):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        try:
            course = Course.objects.get(slug=data_course)
            room = ChatRoom.objects.get(name=room_name, course=course)

            if request.user not in room.members.all():
                room.members.add(request.user)
                
            return JsonResponse({
                'status': 'success',
                'room_name': room_name,
                'course': data_course,
                'message': '成功加入房间'
            }, status=200)
        except Course.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '指定课程不存在'
            }, status=404)
        except ChatRoom.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '房间不存在，请检查房间号！'
            }, status=404)
    return JsonResponse({
        'status': 'error',
        'message': '无效请求'
    }, status=400)


@login_required
def delete_room(request, room_name, data_course):
    try:
        course = Course.objects.get(slug=data_course)
        room = ChatRoom.objects.get(name=room_name, course=course)
        if room.creator == request.user:
            # 当前用户是创建者，可以删除房间
            room.delete()
            return JsonResponse({
                'status': 'success',
                'message': '房间删除成功！'
            }, status=200)
        else:
            # 当前用户不是创建者，无权删除
            return JsonResponse({
                'status': 'error',
                'message': '您无权删除此房间！'
            }, status=403)
    except Course.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '指定课程不存在'
        }, status=404)
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '房间不存在！'
        }, status=404)
    
@login_required
def get_room_list(request, data_course):
    """
    获取当前课程下的所有房间列表（高性能版本）
    """
    try:
        current_user = request.user
        current_user_id = current_user.id  # 提前获取避免重复查询

        # 获取当前课程
        course = Course.objects.get(slug=data_course)

        # 一次性获取所有需要的数据（使用select_related和prefetch_related优化）
        rooms = ChatRoom.objects.filter(course=course) \
                      .select_related('creator') \
                      .prefetch_related('members') \
                      .order_by('-created_at') \
                      .only('name', 'creator_id', 'created_at')  # 只查询必要字段

        # 预加载当前用户加入的所有房间ID（避免N+1查询）
        user_joined_room_ids = set(
            ChatRoom.objects.filter(members=current_user, course=course)
                            .values_list('id', flat=True)
        )

        # 使用批量处理构建响应数据
        room_list = []
        for room in rooms:
            room_list.append({
                'name': room.name,
                'is_creator': room.creator_id == current_user_id,
                'is_member': room.id in user_joined_room_ids,
                'created_at': room.created_at.strftime('%Y-%m-%d %H:%M')
            })

        return JsonResponse({
            'status': 'success',
            'rooms': room_list
        }, status=200)

    except Course.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '指定课程不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': '获取房间列表失败'
        }, status=500)




# def pdf_viewer(request, filename):
#     """渲染自定义 PDF 预览器"""
#     encoded_filename = quote(filename)  # URL 编码，防止空格和特殊字符问题
#     return render(request, 'pdf_viewer.html', {'pdf_url': f"/media/{encoded_filename}"})
#
#
# def generate_thumbnail(pdf_path, thumbnail_path):
#     """从 PDF 第一页生成封面图"""
#     try:
#         doc = fitz.open(pdf_path)
#         page = doc[0]  # 读取第一页
#         pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 提高清晰度
#         pix.save(thumbnail_path)
#     except Exception as e:
#         print(f"生成封面失败: {e}")
#
# def lesson_list(request):
#     """展示所有上传的课程（PDF 第一页缩略图）"""
#     files = []
#     for f in os.listdir(UPLOAD_DIR):
#         if f.endswith('.pdf'):
#             pdf_path = os.path.join(UPLOAD_DIR, f)
#             thumbnail_name = f"{os.path.splitext(f)[0]}.png"
#             thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_name)
#
#             # 如果缩略图不存在，则生成
#             if not os.path.exists(thumbnail_path):
#                 generate_thumbnail(pdf_path, thumbnail_path)
#
#             files.append({
#                 "name": f,
#                 "thumbnail": f"/media/thumbnails/{thumbnail_name}",
#                 "url": f"/preview/{f}"  # ✅ 指向自定义 PDF 预览器
#             })
#
#     return render(request, 'index.html', {'files': files})
#
# def upload_lesson(request):
#     """上传 PDF 课程"""
#     if request.method == 'POST' and request.FILES.get('pdf_file'):
#         pdf_file = request.FILES['pdf_file']
#         if not pdf_file.name.endswith('.pdf'):
#             return JsonResponse({'error': '仅支持 PDF 文件'}, status=400)
#
#         fs = FileSystemStorage(location=UPLOAD_DIR)
#         filename = fs.save(pdf_file.name, pdf_file)
#
#         # 生成封面
#         pdf_path = os.path.join(UPLOAD_DIR, filename)
#         thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{os.path.splitext(filename)[0]}.png")
#         generate_thumbnail(pdf_path, thumbnail_path)
#
#         return redirect('lesson_list')
#
#     return JsonResponse({'error': '无效请求'}, status=400)
#
# def delete_lesson(request):
#     """删除课程 PDF"""
#     if request.method == 'POST':
#         filename = request.POST.get('filename')
#         file_path = os.path.join(UPLOAD_DIR, filename)
#         thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{os.path.splitext(filename)[0]}.png")
#
#         if os.path.exists(file_path):
#             os.remove(file_path)
#         if os.path.exists(thumbnail_path):
#             os.remove(thumbnail_path)
#
#         return JsonResponse({'message': '删除成功'})
#     return JsonResponse({'error': '无效请求'}, status=400)

