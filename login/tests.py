import uuid
from django.test import TestCase
from django.contrib.auth.models import User


class UserLoginTestCase(TestCase):
    def setUp(self):
        self.username = f"loginuser_{uuid.uuid4().hex[:8]}"
        self.password = "testpass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_valid_login(self):
        """测试用户名密码正确可以登录"""
        response = self.client.post("/login/", {
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "IDE/")  # 注意：此处为相对路径，无斜杠

    def test_invalid_login(self):
        """测试用户名或密码错误时不能登录"""
        response = self.client.post("/login/", {
            "username": self.username,
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, 200)
        # 更通用地检查提示内容，不依赖 HTML 标签
        self.assertIn("请输入一个正确的用户名和密码", response.content.decode())



    def test_login_page_get(self):
        """测试 GET 请求可以正常加载登录表单"""
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form', html=False)
