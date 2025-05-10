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
    path('upload-file/', views.upload_file, name='upload_file'),
    path('get-files/', views.get_files, name='get_files'),
    path('delete-file/', views.delete_file, name='delete_file'),
    path('download-file/<str:file_name>/', views.download_file, name='download_file'),
    path('get-tasks/', views.get_tasks, name='get_tasks'),
    path('add-task/', views.add_task, name='add_task'),
    path('toggle-task/', views.toggle_task, name='toggle_task'),
    path('delete-task/', views.delete_task, name='delete_task'),
    path('update-task/', views.update_task, name='update_task'),
]
