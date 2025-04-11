from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse  # ✅ 添加 HttpResponse 以便测试
from .views import embed_chat, deepseek_api, html_to_png


urlpatterns = [
    path('embed_chat/', embed_chat, name='embed_chat'),
    path('api/', deepseek_api, name='deepseek_api'),
    # path('HTP/', html_to_png, name='html_to_png'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# # 允许 Django 在开发模式下提供媒体文件（用户上传的 PDF）
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)