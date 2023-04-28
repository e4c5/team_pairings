import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class Watcher(WebsocketConsumer):
    def connect(self):
        # Join room group
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            'chat', self.channel_name
        )

        

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            'chat', self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data): 
        text_data_json = json.loads(text_data)


        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            'chat', {"type": "chat_message", "message": text_data}
        )

    # Receive message from room group
    def chat_message(self, event):

        # Send message to WebSocket
        self.send(text_data=json.dumps(event['message']))