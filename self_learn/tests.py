import os
import json
import uuid
import pytesseract

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.conf import settings


# 可选：输出 tesseract 版本（用于调试）
# print("Tesseract version:", pytesseract.get_tesseract_version())


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
        os.makedirs(os.path.dirname(self.bookmarks_file), exist_ok=True)
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
