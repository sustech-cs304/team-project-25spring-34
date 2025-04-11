from django.db import models

class State(models.Model):
    is_locked = models.BooleanField(default=False)
    last_user = models.CharField(max_length=150, null=True, blank=True)
