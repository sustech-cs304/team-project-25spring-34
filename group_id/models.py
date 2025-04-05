from django.db import models
from django.conf import settings
from lesson.models import ChatRoom

class RoomFile(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='room_files/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
