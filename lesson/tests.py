from django.test import TestCase, Client
from django.contrib.auth.models import User
import json

class BookmarkTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345678')
        self.client.login(username='testuser', password='12345678')

        self.course = "test_course"
        self.pdf_name = "test.pdf"

        self.bookmark_url = f"/login/IDE/{self.course}/self-learn/add_bookmark/"
        self.get_url = f"/login/IDE/{self.course}/self-learn/get_bookmarks/?pdf_name={self.pdf_name}"
        self.delete_url = f"/login/IDE/{self.course}/self-learn/delete_bookmark/"

    def test_add_and_get_bookmark(self):
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
        self.assertJSONEqual(response.content, {"success": True})

        # 获取书签
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(any(item["description"] == "测试书签" for item in data))

    def test_delete_bookmark(self):
        # 单独添加一次，避免重复写入
        payload = {
            "pdf_name": self.pdf_name,
            "description": "测试书签",
            "category": "重点",
            "page": 1,
            "codeText": "print('hi')"
        }
        self.client.post(self.bookmark_url, json.dumps(payload), content_type="application/json")

        # 删除索引为 0 的书签
        payload = {
            "pdf_name": self.pdf_name,
            "index": 0
        }
        response = self.client.post(self.delete_url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # 验证是否清空
        response = self.client.get(self.get_url)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)


    def test_add_invalid_bookmark(self):
        # 缺少必要字段
        payload = {
            "pdf_name": "",
            "description": "",
            "category": "其他",
            "page": 0
        }
        response = self.client.post(self.bookmark_url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
