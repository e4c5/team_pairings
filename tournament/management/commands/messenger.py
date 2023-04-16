from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

class Command(BaseCommand): 
    '''
    Send messages to various channels or groups
    '''
    
    def add_arguments(self, parser):
        parser.add_argument('--files', nargs='*',
                            help='The list of files that contain the messages to be sent seperated by spaces')
        parser.add_argument('--group', nargs='?', const=True,
                            help='The group to send the message to')
        parser.add_argument('--name', nargs='?', const=True,
                            help='The name of a single channel to send the message to')


    def handle(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)("chat", {
            "type": "chat.message",
            "text": "Hello there!",
        })