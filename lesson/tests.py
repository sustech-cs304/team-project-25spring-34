from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from lesson.models import ChatRoom, ChatMessage

class LessonViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.data_course = 'testcourse'

    def test_lesson_page_renders(self):
        url = reverse('lesson:index', args=[self.data_course])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lesson', response.content.lower())

    def test_hello_view(self):
        url = reverse('lesson:hello', args=[self.data_course])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'hello', response.content.lower())

class ChatRoomModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='roomuser', password='testpass')
        self.room = ChatRoom.objects.create(name='room1', creator=self.user)

    def test_chatroom_creation(self):
        self.assertEqual(self.room.name, 'room1')
        self.assertEqual(self.room.creator, self.user)

    def test_add_member(self):
        self.room.members.add(self.user)
        self.assertIn(self.user, self.room.members.all())

class ChatMessageModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='msguser', password='testpass')
        self.room = ChatRoom.objects.create(name='room2', creator=self.user)
        self.message = ChatMessage.objects.create(room=self.room, user=self.user, content='hello')

    def test_message_content(self):
        self.assertEqual(self.message.content, 'hello')
        self.assertEqual(self.message.room, self.room)
        self.assertEqual(self.message.user, self.user)
# ...可根据 models.py 继续补充其它模型和视图测试...
