from django.db import models

class State(models.Model):
    room_id = models.CharField(max_length=100, unique=True)  # Unique identifier for the room
    is_locked = models.BooleanField(default=False)
    last_user = models.CharField(max_length=150, null=True, blank=True)
    code = models.TextField(default='# 初始代码\nprint("Hello World")')  # 新增代码存储字段
