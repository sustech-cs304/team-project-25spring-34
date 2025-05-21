from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Annotation
from lesson.models import ChatRoom
from IDE.models import Course
import json
import sys
from django.conf import settings

class GroupLearnTests(TransactionTestCase):
    def setUp(self):
        # 数据库配置
        if 'test' in sys.argv:
            self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.sqlite3')
            self.assertTrue('memory' in settings.DATABASES['default']['NAME'].lower())
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            name='Test Course',
            slug='test-course',
            creator=self.user
        )
        
        # 创建测试聊天室
        self.chat_room = ChatRoom.objects.create(
            name='test-room',
            creator=self.user,
            course=self.course
        )
        self.chat_room.members.add(self.user)
        
        # 创建测试标注
        self.annotation = Annotation.objects.create(
            group_id='test-group',
            pdf_url='/test.pdf',
            data={'test': 'data'}
        )
        
        # 创建测试客户端
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_annotation_creation(self):
        """测试标注创建"""
        annotation = Annotation.objects.create(
            group_id='test-group-2',
            pdf_url='/test2.pdf',
            data={'test': 'data2'}
        )
        self.assertEqual(annotation.group_id, 'test-group-2')
        self.assertEqual(annotation.pdf_url, '/test2.pdf')
        self.assertEqual(annotation.data, {'test': 'data2'})

    def test_annotation_str(self):
        """测试标注的字符串表示"""
        expected_str = f"Annotations for Group {self.annotation.group_id} - {self.annotation.pdf_url}"
        self.assertEqual(str(self.annotation), expected_str)

    def test_annotation_data_json(self):
        """测试标注数据的JSON存储"""
        test_data = {
            'page1': {
                'annotations': [
                    {'type': 'pen', 'points': [[100, 100], [200, 200]]}
                ]
            }
        }
        self.annotation.data = test_data
        self.annotation.save()

        loaded_annotation = Annotation.objects.get(id=self.annotation.id)
        self.assertEqual(loaded_annotation.data, test_data)

    def test_annotation_update(self):
        """测试标注更新"""
        new_data = {'updated': 'data'}
        self.annotation.data = new_data
        self.annotation.save()
        
        updated_annotation = Annotation.objects.get(id=self.annotation.id)
        self.assertEqual(updated_annotation.data, new_data)

    def test_annotation_delete(self):
        """测试标注删除"""
        annotation_id = self.annotation.id
        self.annotation.delete()
        
        with self.assertRaises(Annotation.DoesNotExist):
            Annotation.objects.get(id=annotation_id)

    def test_annotation_query(self):
        """测试标注查询"""
        Annotation.objects.create(
            group_id='group1',
            pdf_url='/pdf1.pdf',
            data={'data': '1'}
        )
        Annotation.objects.create(
            group_id='group2',
            pdf_url='/pdf2.pdf',
            data={'data': '2'}
        )

        annotations = Annotation.objects.filter(group_id='group1')
        self.assertEqual(annotations.count(), 1)
        self.assertEqual(annotations.first().pdf_url, '/pdf1.pdf')

    def test_annotation_validation(self):
        """测试标注数据验证"""
        with self.assertRaises(Exception):
            class CircularReference:
                def __init__(self):
                    self.self_reference = self

            invalid_data = CircularReference()
            Annotation.objects.create(
                group_id='invalid-group',
                pdf_url='/test.pdf',
                data=invalid_data
            )

    def test_annotation_relationships(self):
        """测试标注与其他模型的关系"""
        self.assertIsNotNone(self.annotation)
        self.assertIsNotNone(self.chat_room)

        new_annotation = Annotation.objects.create(
            group_id=str(self.chat_room.id),
            pdf_url='/test.pdf',
            data={'test': 'data'}
        )

        annotation2 = Annotation.objects.create(
            group_id=str(self.chat_room.id),
            pdf_url='/test2.pdf',
            data={'test': 'data2'}
        )
        annotations = Annotation.objects.filter(group_id=str(self.chat_room.id))
        self.assertEqual(annotations.count(), 2)
        
        self.chat_room.delete()
        self.assertTrue(Annotation.objects.filter(id=new_annotation.id).exists())
        self.assertTrue(Annotation.objects.filter(id=annotation2.id).exists())

        new_chat_room = ChatRoom.objects.create(
            name='new-room',
            creator=self.user,
            course=self.course
        )
        new_room_annotation = Annotation.objects.create(
            group_id=str(new_chat_room.id),
            pdf_url='/new.pdf',
            data={'test': 'new'}
        )
        self.assertNotEqual(new_annotation.group_id, new_room_annotation.group_id)

    @classmethod
    def setUpClass(cls):
        """在测试类开始前运行"""
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        """在测试类结束后运行"""
        super().tearDownClass()
