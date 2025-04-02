from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # 创建该房间的人
    members = models.ManyToManyField(User, related_name='joined_rooms', blank=True)  # 新增成员字段

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
