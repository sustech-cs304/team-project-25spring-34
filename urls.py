from django.urls import path, include

urlpatterns = [
    path("group_learn/", include("group_learn.urls")),  # 确保包含了 group_learn 的路由
    path("login/IDE/lesson/group_learn/", include("group_learn.urls")),  # 添加路径前缀
]