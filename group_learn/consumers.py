import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from lesson.models import ChatRoom, ChatMessage

# Receive message from WebSocket
get_room = sync_to_async(ChatRoom.objects.get)
create_message = sync_to_async(ChatMessage.objects.create)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_id = None
        self.room_group_name = None
        self.user = None

    async def connect(self):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.room_group_name = f"group-{self.group_id}"
        if not self.group_id:
            print("Room name not found!")
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            print('未登录')
            # await self.accept()
            # await self.send(text_data=json.dumps({'code': '201', 'msg':'请先登录'}))
            await self.close()
            return
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # 异步方式获取房间对象
        room = await get_room(name=self.group_id)
        # 异步方式创建聊天消息
        await create_message(room=room, user=self.user, content=message)
        # Send message to room group
        # print("打印：" + self.user.username)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", 'message': self.user.username + " : " + message, }
        )

    # Receive message from room group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
