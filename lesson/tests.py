from django.test import TestCase, Client
from django.contrib.auth.models import User
import json
import uuid
import os
from django.conf import settings



from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from IDE.models import Course
from lesson.models import ChatRoom
from lesson import views
import uuid
import json


class ChatRoomTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.username = f"user_{uuid.uuid4().hex[:8]}"
        self.user = User.objects.create_user(username=self.username, password='12345678')
        self.course = Course.objects.create(name="测试课程", slug="test-course", creator=self.user)
        self.course_slug = self.course.slug
        self.room_name = "testroom"

    def test_create_room(self):
        request = self.factory.post("/", data={"room_name": self.room_name})
        request.user = self.user
        response = views.create_room(request, self.course_slug)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertTrue(ChatRoom.objects.filter(name=self.room_name, course=self.course).exists())

    def test_join_room(self):
        room = ChatRoom.objects.create(name=self.room_name, course=self.course, creator=self.user)
        new_user = User.objects.create_user(username="other_user", password="abc123456")
        request = self.factory.post("/", data={"room_name": self.room_name})
        request.user = new_user
        response = views.join_room(request, self.course_slug)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertIn(new_user, room.members.all())

    def test_delete_room_as_creator(self):
        ChatRoom.objects.create(name=self.room_name, course=self.course, creator=self.user)
        request = self.factory.get("/")
        request.user = self.user
        response = views.delete_room(request, self.room_name, self.course_slug)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertFalse(ChatRoom.objects.filter(name=self.room_name, course=self.course).exists())



