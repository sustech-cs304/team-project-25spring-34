"""
URL configuration for IDEframework project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from login import views as login_views
from register import views as register_views
from IDE import views as IDE_views
from group_id import views as group_id_views
from group_learn import views as group_learn_views

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/IDE/', include([
        path('', IDE_views.index),
        path('', include('IDE.urls')),
        path('<str:data_course>/', include([  # lesson/
            path('', IDE_views.course_view, name='course_view'),
            path('', include('lesson.urls')),
            path('self-learn/', include('self_learn.urls')),
            path('deepseek-chat/', include('ai_assistant.urls')),  # 新增聊天应用路由
            path('group-<str:group_id>/', include([
                path('', include('group_id.urls')),
                path('group-learn/', group_learn_views.index),
                path('group-learn/save_annotations/', group_learn_views.save_annotations, name='save_annotations'),
                path('group-learn/get_annotations/', group_learn_views.get_annotations, name='get_annotations'),
                path('group-learn/', include('group_learn.urls')),
            ]))
        ]))
    ])),
    path('login/', login_views.user_login, name='login'),
    path('register/', register_views.user_register, name='register'),
    path('group_id/', group_id_views.group_id, name='group_id'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
