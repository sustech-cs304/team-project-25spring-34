from django.urls import path
from . import views

app_name = 'group_id'

urlpatterns = [
    path("", views.index, name="index"),
    # 离开小组接口
    path('leave-room/', views.leave_room, name='leave_room'),
    # 获取成员列表接口（供前端轮询）
    path('get-members/', views.get_members, name='get_members'),
    path('validate-room/', views.validate_room, name='validate-room'),
    path('update-topic/', views.update_topic, name='update-topic'),
    path('get-learning-topics/', views.get_learning_topics, name='get-learning-topics'),
]
