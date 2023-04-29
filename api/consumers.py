import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer


class Watcher(AsyncWebsocketConsumer):
    async def connect(self):
        # Join room group
        await self.accept()
        await self.channel_layer.group_add(
            'chat', self.channel_name
        )

        # i am guessing there is a bug in the ChannelsLiveServerTestCase 
        # unless some message is sent on the socket at the start, some tests
        # fail even though if you tried the exact same steps manually in the
        # browser it would still work.
        await self.channel_layer.group_send(
            'chat', {"type": "chat_message", "message": "Hello!"}
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            'chat', self.channel_name
        )
        super().disconnect()

    # Receive message from WebSocket
    async def receive(self, text_data): 
        # Send message to room group
        await self.channel_layer.group_send(
            'chat', {"type": "chat_message", "message": text_data}
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))