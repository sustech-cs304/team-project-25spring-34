from django.db import models
from django.contrib.auth.models import User
from IDE.models import Course

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)  # 移除 unique=True
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='joined_rooms', blank=True)
    current_pdf = models.ForeignKey(
        'group_id.RoomFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_rooms'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_rooms'
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('name', 'course')]  # name 和 course 组合唯一

    def __str__(self):
        return self.name

    def add_member(self, user):
        """添加成员到房间"""
        self.members.add(user)
        self.save()

    def remove_member(self, user):
        """从房间移除成员"""
        self.members.remove(user)
        self.save()

    @property
    def group_id(self):
        """返回房间ID作为group_id"""
        return self.id

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'
