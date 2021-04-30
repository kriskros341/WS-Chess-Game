import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
import json
import uuid
import time
PORT = 2137
connList = []
rectList = []


class Rectangle():
    def __init__(self, conn, x, y):
        self.conn = conn
        self.x = x
        self.y = y
        self.id = 0
        rectList.append(self)

    def move_to(self, coords):
        self.x = coords['x']
        self.y = coords['y']

class getId(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        self.write(uuid.uuid4().hex)

class Player(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rect = Rectangle(self, 500, 500)
        connList.append(self)

    def check_origin(self, origin):
        return True

    def on_open(self):
        pass

    def on_message(self, message):
        data = json.loads(message)
        print(data)
        if self.rect.id == 0:
            self.rect.id = data['id']
        for x in rectList:
            if x.conn == self:
                x.move_to(data)
        for y in connList:
            y.write_message(json.dumps([{"id": x.id, "data": [x.x, x.y]} for x in rectList]))

    def on_close(self):
        rectList.pop(rectList.index(self.rect))
        connList.pop(connList.index(self))


def make_app():
    return tornado.web.Application([
        (r"/getId", getId),
        (r"/kwadrat", Player),

    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    print(f"Listening localhost on {PORT}")
    tornado.ioloop.IOLoop.current().start()

