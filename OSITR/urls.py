from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse  # ✅ 添加 HttpResponse 以便测试
from .views import upload_pdf, view_bookmarks, select_area, preprocess_image  # ✅ 直接导入 views.py

# ✅ 添加一个简单的首页视图
def home_view(request):
    return HttpResponse("<h1>Welcome to PDF Manager</h1><p>Go to <a href='/pdf/viewer/'>Viewer</a> to browse PDFs.</p>")

urlpatterns = [
    path("pdf/upload/", upload_pdf, name="upload-pdf"),
    path("pdf/viewer/", view_bookmarks, name="viewer"),
    path("pdf/select_area/", select_area, name='select_area'),
    path("pdf/preprocess_image/", preprocess_image, name='preprocess_image'),
    # ✅ 添加根路径 `/`
    path("", home_view, name="home"),
]

# ✅ 让 Django 访问上传的 media 文件（PDF、图片）
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)