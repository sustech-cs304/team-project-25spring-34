import uuid
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class UserRegisterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.valid_data = {
            "username": self.username,
            "password1": "Testpassword123",
            "password2": "Testpassword123",
        }

    def test_register_success(self):
        response = self.client.post(self.register_url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=self.username).exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username=self.username, password="dummy")
        response = self.client.post(self.register_url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<ul class="errorlist">', html=False)

    def test_register_password_mismatch(self):
        data = self.valid_data.copy()
        data["password2"] = "Mismatch123"
        response = self.client.post(self.register_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<ul class="errorlist">', html=False)

    def test_register_password_too_short(self):
        data = self.valid_data.copy()
        data["password1"] = data["password2"] = "123"
        response = self.client.post(self.register_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<ul class="errorlist">', html=False)
