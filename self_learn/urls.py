from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from .views import (index, select_area, preprocess_image,
                    upload_pdf, view_bookmarks, run_code,
                    get_pdf_list, get_bookmarks, add_bookmark,delete_pdf,
                    delete_bookmark, intelligent_preprocess_image,
                    save_annotations, get_annotations)  # 新增


urlpatterns = [
    path('', index),
    path("select_area/", select_area, name='select_area'),
    path("preprocess_image/", preprocess_image, name='preprocess_image'),
    path("intelligent_preprocess_image/", intelligent_preprocess_image, name='intelligent_preprocess_image'),
    path("pdf/viewer/", view_bookmarks, name="viewer"),
    path('run/', run_code, name='run_code'), # 执行代码的接口
    path('upload_pdf/', upload_pdf, name='upload_pdf'),
    path('delete_pdf/', delete_pdf, name='delete_pdf'),
    path('save_annotations/', save_annotations, name='save_annotations'),  # 新增
    path('get_annotations/', get_annotations, name='get_annotations'),    # 新增
]

urlpatterns += [
    path('get_pdf_list/', get_pdf_list, name='get_pdf_list'),
    path('get_bookmarks/', get_bookmarks, name='get_bookmarks'),
    path('add_bookmark/', add_bookmark, name='add_bookmark'),
    path('delete_bookmark/', delete_bookmark, name='delete_bookmark'),
]

# # 允许 Django 在开发模式下提供媒体文件（用户上传的 PDF）
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
