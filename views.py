import os
import sys
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings  # ✅ 让 Django 读取 settings.py 里的 MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt

# ✅ 直接指定 pdf_handler.py 的绝对路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  

# ✅ 确保正确导入 process_pdf
from pdf_handler import process_pdf  

@csrf_exempt
def upload_pdf(request):
    """上传 PDF 并转换为图片"""
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        bookmarks = process_pdf(pdf_file)  # ✅ 调用 process_pdf 处理 PDF
        return JsonResponse({"message": "PDF uploaded successfully", "bookmarks": bookmarks})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def view_bookmarks(request):
    """展示 PDF 转换后的页面"""
    img_folder = os.path.join(settings.MEDIA_ROOT, "pdf_images")  # ✅ 使用 settings.MEDIA_ROOT
    img_files = sorted(f for f in os.listdir(img_folder) if f.endswith(".jpg"))
    bookmarks = {i+1: f"/media/pdf_images/{img}" for i, img in enumerate(img_files)}
    
    return render(request, "viewer.html", {"bookmarks": bookmarks})
