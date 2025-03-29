from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse  # ✅ 添加 HttpResponse 以便测试

from . import views
from .views import *


urlpatterns = [
    path('', views.index, name='index'),  # 主页面
    path("select_area/", select_area, name='select_area'),
    path("preprocess_image/", preprocess_image, name='preprocess_image'),
    # path("pdf/upload/", upload_pdf, name="upload-pdf"),
    path("pdf/viewer/", view_bookmarks, name="viewer"),
    path('run/', views.run_code, name='run_code'), # 执行代码的接口
]

# # 允许 Django 在开发模式下提供媒体文件（用户上传的 PDF）
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)