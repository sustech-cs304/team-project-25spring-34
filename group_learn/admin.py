from django.contrib import admin
from lesson.models import ChatRoom, ChatMessage

# 注册模型到Django管理后台
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)