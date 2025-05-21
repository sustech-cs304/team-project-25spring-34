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



class BookmarkTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # ✅ 每次用唯一用户名避免污染
        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.user = User.objects.create_user(username=self.username, password='12345678')
        self.client.login(username=self.username, password='12345678')

        self.course = "test_course"
        self.pdf_name = "test.pdf"

        self.bookmark_url = f"/login/IDE/{self.course}/self-learn/add_bookmark/"
        self.get_url = f"/login/IDE/{self.course}/self-learn/get_bookmarks/?pdf_name={self.pdf_name}"
        self.delete_url = f"/login/IDE/{self.course}/self-learn/delete_bookmark/"

        # ✅ 每次手动清空用户书签文件，防止之前添加的数据影响当前测试
        self.bookmarks_file = os.path.join(settings.MEDIA_ROOT, 'bookmarks', self.course, self.username, 'bookmarks.json')
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, 'w') as f:
                json.dump({}, f)

    def test_add_and_get_bookmark(self):
        payload = {
            "pdf_name": self.pdf_name,
            "description": "测试书签",
            "category": "重点",
            "page": 1,
            "codeText": "print('hi')"
        }
        response = self.client.post(self.bookmark_url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(any(item["description"] == "测试书签" for item in data))

    def test_delete_bookmark(self):
        # 添加书签
        payload = {
            "pdf_name": self.pdf_name,
            "description": "测试书签",
            "category": "重点",
            "page": 1,
            "codeText": "print('hi')"
        }
        response = self.client.post(self.bookmark_url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # 删除书签
        response = self.client.post(self.delete_url, json.dumps({
            "pdf_name": self.pdf_name,
            "index": 0
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # 再次获取，应该为空
        response = self.client.get(self.get_url)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_add_invalid_bookmark(self):
        payload = {
            "pdf_name": "",
            "description": "",
            "category": "其他",
            "page": 0
        }
        response = self.client.post(self.bookmark_url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
