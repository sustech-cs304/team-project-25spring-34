import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from lesson.models import ChatRoom, ChatMessage
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# 异步获取房间对象，考虑course_name
get_room = sync_to_async(lambda room_name, course_name: ChatRoom.objects.get(name=room_name, course__slug=course_name))
create_message = sync_to_async(ChatMessage.objects.create)


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.course_name = None
        self.room_group_name = None
        self.user = None
        self.room = None

    async def connect(self):
        try:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.course_name = self.scope["url_route"]["kwargs"]["course_name"]

            if not self.room_name or not self.course_name:
                print("Room name or course name not found!")
                await self.close()
                return

            # 获取房间对象，同时验证course_name
            self.room = await get_room(self.room_name, self.course_name)
            self.room_group_name = f"group-{self.room.id}"  # 使用房间ID作为唯一group名称

            # 检查用户权限
            self.user = self.scope["user"]
            if not self.user.is_authenticated:
                print('User not authenticated')
                await self.close()
                return

            # 检查用户是否是房间成员
            if not await sync_to_async(lambda: self.user in self.room.members.all())():
                print(f'User {self.user.username} is not a member of room {self.room_name}')
                await self.close()
                return

            # 加入房间组
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

        except KeyError as e:
            print(f"Missing required parameter: {e}")
            await self.close()
        except ObjectDoesNotExist:
            print(f"Room {self.room_name} with course {self.course_name} not found!")
            await self.close()
        except MultipleObjectsReturned:
            print(f"Multiple rooms found with name {self.room_name} - course name required!")
            await self.close()
        except Exception as e:
            print(f"Unexpected error during connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        # 离开房间组
        if hasattr(self, 'room_group_name') and self.room_group_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            # 创建聊天消息
            await create_message(room=self.room, user=self.user, content=message)

            # 准备发送的消息
            message_data = {
                'type': 'chat.message',
                'message': f"{self.user.username}: {message}",
                'user_id': self.user.id,
                'username': self.user.username,
                'timestamp': str(self.room.last_updated)
            }

            # 发送消息到房间组
            await self.channel_layer.group_send(
                self.room_group_name,
                message_data
            )
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except KeyError as e:
            print(f"Missing key in message: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")

    # 接收来自房间组的消息
    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            print(f"Error sending message: {e}")