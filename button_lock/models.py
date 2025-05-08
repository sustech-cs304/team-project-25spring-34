from django.db import models

class State(models.Model):
    room_id = models.CharField(max_length=100, unique=True)  # Unique identifier for the room
    is_locked = models.BooleanField(default=False)
    last_user = models.CharField(max_length=150, null=True, blank=True)
