from django.test import TestCase, Client
from django.contrib.auth.models import User
from IDE.models import Course
from django.urls import reverse
import json


class CourseViewTest(TestCase):

    def setUp(self):
        # 创建用户（普通用户和管理员）
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.admin = User.objects.create_user(username='admin', password='admin')

        # 创建 Client 实例用于发送请求
        self.client = Client()

        # 创建一个已有课程
        self.course = Course.objects.create(name='Math 101', slug='math-101', creator=self.admin)

    def test_get_courses_requires_login(self):
        response = self.client.get(reverse('IDE:get_courses'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_get_courses_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('IDE:get_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('courses', response.json())

    def test_add_course_success(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'name': 'Physics 101'
        }
        response = self.client.post(
            reverse('IDE:add_course'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertTrue(Course.objects.filter(slug='physics-101').exists())

    def test_add_course_duplicate(self):
        self.client.login(username='admin', password='admin')
        data = {
            'name': 'Math 101'  # 已存在
        }
        response = self.client.post(
            reverse('IDE:add_course'),
            data=json.dumps(data),
            content_type='application/json'
        )
        print("test_add_course_duplicate Response JSON:", response.json())
        print("test_add_course_duplicate Response content:", response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Course already exists')

    def test_add_course_invalid_json(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('IDE:add_course'),
            data='invalid json',
            content_type='application/json'
        )
        print("test_add_course_invalid_json Response JSON:", response.json())
        print("test_add_course_invalid_json Response content:", response.content)
        self.assertEqual(response.status_code, 400)

    def test_delete_course_permission_denied(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('IDE:delete_course'),
            data=json.dumps({'slug': 'math-101'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_course_success(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(
            reverse('IDE:delete_course'),
            data=json.dumps({'slug': 'math-101'}),
            content_type='application/json'
        )
        print("Response JSON:", response.json())
        print("Response content:", response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertFalse(Course.objects.filter(slug='math-101').exists())

    def test_delete_course_not_found(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(
            reverse('IDE:delete_course'),
            data=json.dumps({'slug': 'not-exist'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
