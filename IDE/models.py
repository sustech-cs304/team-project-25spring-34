from django.db import models
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 课程名称
    slug = models.SlugField(max_length=100, unique=True)  # URL友好的标识
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # 创建者
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def course_id(self):
        """返回课程ID作为course_id"""
        return self.id