import os
import fitz  # PyMuPDF
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
THUMBNAIL_DIR = os.path.join(UPLOAD_DIR, 'thumbnails')

# 确保缩略图目录存在
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

from urllib.parse import quote


from django.views.decorators.csrf import csrf_exempt





def pdf_viewer(request, filename):
    """渲染自定义 PDF 预览器"""
    encoded_filename = quote(filename)  # URL 编码，防止空格和特殊字符问题
    return render(request, 'pdf_viewer.html', {'pdf_url': f"/media/{encoded_filename}"})


def generate_thumbnail(pdf_path, thumbnail_path):
    """从 PDF 第一页生成封面图"""
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]  # 读取第一页
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 提高清晰度
        pix.save(thumbnail_path)
    except Exception as e:
        print(f"生成封面失败: {e}")

def lesson_list(request):
    """展示所有上传的课程（PDF 第一页缩略图）"""
    files = []
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith('.pdf'):
            pdf_path = os.path.join(UPLOAD_DIR, f)
            thumbnail_name = f"{os.path.splitext(f)[0]}.png"
            thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_name)

            # 如果缩略图不存在，则生成
            if not os.path.exists(thumbnail_path):
                generate_thumbnail(pdf_path, thumbnail_path)

            files.append({
                "name": f,
                "thumbnail": f"/media/thumbnails/{thumbnail_name}",
                "url": f"/preview/{f}"  # ✅ 指向自定义 PDF 预览器
            })

    return render(request, 'index.html', {'files': files})

def upload_lesson(request):
    """上传 PDF 课程"""
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        if not pdf_file.name.endswith('.pdf'):
            return JsonResponse({'error': '仅支持 PDF 文件'}, status=400)

        fs = FileSystemStorage(location=UPLOAD_DIR)
        filename = fs.save(pdf_file.name, pdf_file)

        # 生成封面
        pdf_path = os.path.join(UPLOAD_DIR, filename)
        thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{os.path.splitext(filename)[0]}.png")
        generate_thumbnail(pdf_path, thumbnail_path)

        return redirect('lesson_list')

    return JsonResponse({'error': '无效请求'}, status=400)

def delete_lesson(request):
    """删除课程 PDF"""
    if request.method == 'POST':
        filename = request.POST.get('filename')
        file_path = os.path.join(UPLOAD_DIR, filename)
        thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{os.path.splitext(filename)[0]}.png")

        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

        return JsonResponse({'message': '删除成功'})
    return JsonResponse({'error': '无效请求'}, status=400)
