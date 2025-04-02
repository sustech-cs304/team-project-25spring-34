import os
import fitz  # PyMuPDF
from urllib.parse import quote
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage

def index(request):
    return render(request, 'lesson.html')

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import ChatRoom

def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        # 检查房间是否已存在
        if ChatRoom.objects.filter(name=room_name).exists():
            return HttpResponse('group已存在，请使用其他名称！', status=400)
        else:
            # 创建新房间
            new_room = ChatRoom.objects.create(name=room_name, creator=request.user)
            new_room.members.add(request.user)  # 强制将leader放入members中
            # 返回成功响应
            return HttpResponse(f'group "{room_name}" 创建成功！', status=201)
    return redirect('index')

def join_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        print(room_name)
        room = ChatRoom.objects.get(name=room_name)
        print(room)
        if ChatRoom.objects.filter(name=room_name).exists():
            room.members.add(request.user)
            return JsonResponse({'status': 'success', 'room_name': room_name}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'group不存在，请检查房间号！'}, status=404)
    return JsonResponse({'status': 'error', 'message': '无效请求'}, status=400)

def delete_room(request, room_name):
    try:
        room = ChatRoom.objects.get(name=room_name)
        print(room.creator)
        if room.creator == request.user:
            # 当前用户是创建者，可以删除房间
            room.delete()
            return JsonResponse({'status': 'success', 'message': '房间删除成功！'}, status=200)
        else:
            # 当前用户不是创建者，无权删除
            return JsonResponse({'status': 'error', 'message': '您无权删除此房间！'}, status=403)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '房间不存在！'}, status=404)




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

