from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse  # ✅ 添加 HttpResponse 以便测试
from .views import select_area, preprocess_image  # ✅ 直接导入 views.py

urlpatterns = [
    path("login/IDE/lesson/self-learn/select_area/", select_area, name='select_area'),
    path("login/IDE/lesson/self-learn/preprocess_image/", preprocess_image, name='preprocess_image'),
]
