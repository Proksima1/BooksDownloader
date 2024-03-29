from channels.generic.websocket import WebsocketConsumer
import json
from .tasks import parseBooksTask, searchBooksTask, getPageTask
from asgiref.sync import async_to_sync


class WSSearch(WebsocketConsumer):
    def __init__(self):
        super(WSSearch, self).__init__()
        self.receiveTypes = {'search': searchBooksTask,
                             'parse': parseBooksTask,
                             'goToPage': getPageTask}

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            "booksGroup",
            self.channel_name,
        )
        self.accept()
        self.send(json.dumps({'type': 'welcome',
                              'message': 'Hello, you are connected'}))

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        messageType = data['type']
        print(f'Got message: {data}')
        task = self.receiveTypes[messageType].delay(data['message'])

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            "booksGroup", self.channel_name
        )

    def send_data(self, event):
        print(f'Sent message: {event["message"][0:100]}...')
        self.send(text_data=event["message"])
