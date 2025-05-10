from django.db import models
from django.conf import settings
from lesson.models import ChatRoom

class RoomFile(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)
    file_data = models.BinaryField(default=b'')  
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='tasks')
    text = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    category = models.CharField(max_length=50, default='normal')  # 'urgent', 'normal', 'low'
    created_at = models.DateTimeField(auto_now_add=True)
