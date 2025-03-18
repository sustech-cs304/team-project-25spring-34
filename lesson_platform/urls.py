from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import lesson_list, upload_lesson, delete_lesson, pdf_viewer

urlpatterns = [
    path('', lesson_list, name='lesson_list'),
    path('upload/', upload_lesson, name='upload_lesson'),
    path('delete/', delete_lesson, name='delete_lesson'),
    path('preview/<str:filename>/', pdf_viewer, name='pdf_viewer'),  # ✅ 自定义 PDF 预览器
]

# 允许 Django 在开发模式下提供媒体文件（用户上传的 PDF）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
