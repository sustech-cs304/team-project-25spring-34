from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from lesson.models import ChatRoom, Course
from group_id.models import RoomFile, Task
from django.core.cache import cache
import json
from io import BytesIO

class GroupIdViewsTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        
        # 创建测试课程
        self.course = Course.objects.create(
            slug='test-course', 
            name='Test Course',
            creator=self.user1
        )
        
        # 创建测试聊天室
        self.room = ChatRoom.objects.create(
            name='test-group',
            course=self.course,
            creator=self.user1
        )
        self.room.members.add(self.user1)
        
        # 初始化客户端
        self.client = Client()
        
        # 登录用户
        self.client.force_login(self.user1)
        
        # 设置测试缓存
        cache.set(f"chat_room_topic_test-group", "Initial topic", timeout=86400)
    
    # 测试index视图
    def test_index_view(self):
        response = self.client.get(reverse('group_id:index', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group-id.html')
    
    # 测试get_members视图
    def test_get_members_success(self):
        response = self.client.get(reverse('group_id:get_members', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['members']), 1)
    
    def test_get_members_permission_denied(self):
        self.client.force_login(self.user2)
        response = self.client.get(reverse('group_id:get_members', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 403)
    
    def test_get_members_room_not_exist(self):
        response = self.client.get(reverse('group_id:get_members', kwargs={
            'data_course': 'invalid-course',
            'group_id': 'invalid-group'
        }))
        self.assertEqual(response.status_code, 404)
    
    # 测试leave_room视图
    def test_leave_room_success(self):
        response = self.client.post(reverse('group_id:leave_room', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertFalse(self.user1 in self.room.members.all())
    
    def test_leave_room_not_member(self):
        self.client.force_login(self.user2)
        response = self.client.post(reverse('group_id:leave_room', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 403)
    
    # 测试get_learning_topics视图
    def test_get_learning_topics(self):
        response = self.client.post(reverse('group_id:get-learning-topics', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['topics'], 'Initial topic')
    
    def test_get_learning_topics_not_member(self):
        self.client.force_login(self.user2)
        response = self.client.post(reverse('group_id:get-learning-topics', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 403)
    
    # 测试validate_room视图
    def test_validate_room_success(self):
        response = self.client.post(reverse('group_id:validate-room', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['is_valid'])
    
    def test_validate_room_not_member(self):
        self.client.force_login(self.user2)
        response = self.client.post(reverse('group_id:validate-room', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 403)
    
    # 测试update_topic视图
    def test_update_topic_success(self):
        response = self.client.post(
            reverse('group_id:update-topic', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'topic': 'New topic'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(cache.get(f"chat_room_topic_test-group"), 'New topic')
    
    def test_update_topic_not_creator(self):
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse('group_id:update-topic', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'topic': 'New topic'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_update_topic_empty(self):
        response = self.client.post(
            reverse('group_id:update-topic', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'topic': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    # 测试upload_file视图
    def test_upload_file_success(self):
        test_file = BytesIO(b'Test file content')
        test_file.name = 'test.txt'
        
        response = self.client.post(reverse('group_id:upload_file', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }), {'file': test_file})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(RoomFile.objects.filter(file_name='test.txt').exists())
    
    def test_upload_file_duplicate(self):
        # 先上传一个文件
        RoomFile.objects.create(
            room=self.room,
            file_name='test.txt',
            file_data=b'Test content',
            uploaded_by=self.user1
        )
        
        test_file = BytesIO(b'Test file content')
        test_file.name = 'test.txt'
        
        response = self.client.post(reverse('group_id:upload_file', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }), {'file': test_file})
        self.assertEqual(response.status_code, 400)
    
    # 测试get_files视图
    def test_get_files_success(self):
        # 先上传一个文件
        RoomFile.objects.create(
            room=self.room,
            file_name='test.txt',
            file_data=b'Test content',
            uploaded_by=self.user1
        )
        
        response = self.client.get(reverse('group_id:get_files', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['files']), 1)
    
    # 测试delete_file视图
    def test_delete_file_success(self):
        # 先上传一个文件
        file = RoomFile.objects.create(
            room=self.room,
            file_name='test.txt',
            file_data=b'Test content',
            uploaded_by=self.user1
        )
        
        response = self.client.post(
            reverse('group_id:delete_file', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'file_name': 'test.txt'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RoomFile.objects.filter(id=file.id).exists())
    
    def test_delete_file_not_exist(self):
        response = self.client.post(
            reverse('group_id:delete_file', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'file_name': 'nonexistent.txt'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    # 测试download_file视图
    def test_download_file_success(self):
        # 先上传一个文件
        file = RoomFile.objects.create(
            room=self.room,
            file_name='test.txt',
            file_data=b'Test content',
            uploaded_by=self.user1
        )
        
        response = self.client.get(reverse('group_id:download_file', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group',
            'file_name': 'test.txt'
        }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'Test content')
    
    # 测试get_tasks视图
    def test_get_tasks_success(self):
        # 创建一个任务
        Task.objects.create(
            room=self.room,
            text='Test task',
            category='normal'
        )
        
        response = self.client.get(reverse('group_id:get_tasks', kwargs={
            'data_course': 'test-course',
            'group_id': 'test-group'
        }))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['tasks']), 1)
    
    # 测试add_task视图
    def test_add_task_success(self):
        response = self.client.post(
            reverse('group_id:add_task', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'text': 'New task', 'category': 'important'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(Task.objects.filter(text='New task').exists())
    
    def test_add_task_empty_text(self):
        response = self.client.post(
            reverse('group_id:add_task', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'text': '', 'category': 'important'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    # 测试toggle_task视图
    def test_toggle_task_success(self):
        task = Task.objects.create(
            room=self.room,
            text='Test task',
            completed=False
        )
        response = self.client.post(
            reverse('group_id:toggle_task', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'task_id': task.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertTrue(task.completed)
    
    def test_toggle_task_not_exist(self):
        response = self.client.post(
            reverse('group_id:toggle_task', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'task_id': 999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    # 测试update_task视图
    def test_update_task_success(self):
        task = Task.objects.create(
            room=self.room,
            text='Old text',
            category='normal'
        )
        response = self.client.post(
            reverse('group_id:update_task', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'task_id': task.id, 'text': 'Updated text', 'category': 'important'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.text, 'Updated text')
        self.assertEqual(task.category, 'important')
    
    def test_update_task_empty_text(self):
        task = Task.objects.create(
            room=self.room,
            text='Old text',
            category='normal'
        )
        response = self.client.post(
            reverse('group_id:update_task', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'task_id': task.id, 'text': '', 'category': 'important'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    # 测试delete_task视图
    def test_delete_task_success(self):
        task = Task.objects.create(
            room=self.room,
            text='Task to delete'
        )
        
        response = self.client.post(
            reverse('group_id:delete_task', kwargs={
                'data_course': 'test-course',
                'group_id': 'test-group'
            }),
            data=json.dumps({'task_id': task.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(id=task.id).exists())