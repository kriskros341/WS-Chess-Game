import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
import json
import uuid
PORT = 3333
connList = []
gameList = []

pawn_moves = {"w": [(1, 0)], "b": [(-1, 0)]}
pawn_attacks = {"w": [(1, 1), (1, -1)], "b": [(-1, 1), (-1, -1)]}

piece_n_n = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)]
piece_n_0 = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
             (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]


def sendData(data, state):
    this_game = next(x for x in gameList if x.id == data['gameId'])
    for conn in [p.conn for p in this_game.players]:
        conn.write_message(json.dumps({"state": state, "reason": "requested", "gameId": this_game.id,
                                       "game_state": [x.to_json() for x in this_game.board.tiles]}))


def validate_move_old(game, piece, from_where, to_where):
    from_where[0] = int(from_where[0])*-1
    move = ((int(from_where[0])+int(to_where[0])),int(from_where[1])-int(to_where[1]))
    print(move[0], move[1])
    print(from_where[0])
    if piece == 'w_pawn' or piece == "b_pawn":
        print((from_where[0] == 2 or from_where[0] == 7) and (move[0] == 2 or move[0] == -2) )
        if (-1*from_where[0] == 2 or -1*from_where[0] == 7) and (move[0] == 2 or move[0] == -2) and (move[1] == 0 or move[1] == 0):
            return True
        elif (move in pawn_moves['w'] or move in pawn_moves['b'] or move in pawn_attacks['w'] or move in pawn_attacks['b']):
            return True
        else:
            print("blad!!!")
            return False
    return True
    print(game)
    print(piece)
    print(to)

    return True


def new_player_join(game_id):
    if game_id in [game.id for game in gameList if len(game.players) < 2]:
        p = Player(None)
        p.join_game([game for game in gameList if game.id == game_id][0])
    else:
        print('game either full or not found')


class Piece:
    def __init__(self, color):
        self.tile = None
        self.color = color
        pass

    def get_ign(self):
        return f"{self.color}_{self.name}"

    def to_str(self):
        return self.get_ign()


class Pawn(Piece):
    def __init__(self, color, *args, **kwargs):
        super().__init__(color, *args, **kwargs)
        self.name = "pawn"
        self.moves = {"w": [(-1, 0)], "b": [(1, 0)]}
        self.attacks = {"w": [(1, 1), (1, -1)], "b": [(-1, 1), (-1, -1)]}
        self.ign = self.get_ign()

    def upgrade(self):
        pass


class Tower(Piece):
    def __init__(self, color, *args, **kwargs):
        super().__init__(color, *args, **kwargs)
        self.name = "tower"
        self.moves = piece_n_0
        self.ign = self.get_ign()

class Bishop(Piece):
    def __init__(self, color, *args, **kwargs):
        super().__init__(color, *args, **kwargs)
        self.name = "bishop"
        self.moves = piece_n_n
        self.ign = self.get_ign()

class Horseman(Piece):
    def __init__(self, color, *args, **kwargs):
        super().__init__(color, *args, **kwargs)
        self.moves = [(2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (1, -2), (-1, -2)]
        self.name = "horseman"
        self.ign = self.get_ign()

class King(Piece):
    def __init__(self, color, *args, **kwargs):
        super().__init__(color, *args, **kwargs)
        self.moves = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        self.name = "King"
        self.ign = self.get_ign()

class Queen(Piece):
    def __init__(self, color, *args, **kwargs):
        super().__init__(color, *args, **kwargs)
        self.moves = piece_n_0 + piece_n_n
        self.name = "Queen"
        self.ign = self.get_ign()

class Game:
    def __init__(self):
        self.turn_of = None
        gameList.append(self)
        self.players = []
        self.settings = {}
        self.length = 0
        self.id = uuid.uuid4().hex
        self.board = Board()

    def join(self, player):
        self.players.append(player)

    def next_player(self):
        if len(self.players) < 2:
            print("there is no other player in the lobby idiot!")
            return
        if self.turn_of == None:
            self.turn_of = self.players[0]
        if self.turn_of == self.players[0]:
            self.turn_of = self.players[1]
        if self.turn_of == self.players[1]:
            self.turn_of = self.players[0]

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coords = (x, y)
        self.piece = None

    def set_piece(self, piece):
        self.piece = piece

    def to_json(self):
        if self.piece:
            return json.dumps({"tile": (self.x, self.y), "piece": self.piece.ign})
        else:
            return json.dumps({"tile": (self.x, self.y), "piece": None})



class Board:
    def __init__(self):
        self.tiles = [Tile(x, y) for x in range(1, 9) for y in range(1, 9)]
        print(f"new board: {self}")

    def is_path_obstructed(self, from_tile_coords, to_tile_coords, vector):
        print(from_tile_coords, to_tile_coords)
        print("wektor: ", vector[0], vector[1])
        if abs(vector[0]) == abs(vector[1]):
            for x in range(vector[0]+1):
                print((from_tile_coords[0]-x, from_tile_coords[1]-x))
                #print(self.get_tile_object((from_tile_coords[0]+x, from_tile_coords[1]+x)))
                #x/abs(x) will give me 1 or -1
                #y/abs(y) will give me 1 or -1
                #but I dont want to do it right now i feel lazy

        if vector[0] == 0:
            return True
        if vector[1] == 0:
            return True


    def validate_move(self, from_tile_coords, to_tile_coords):
        from_tile_object = self.get_tile_object(from_tile_coords)
        to_tile_object = self.get_tile_object(to_tile_coords)
        vector = (from_tile_coords[0] - to_tile_coords[0], from_tile_coords[1] - to_tile_coords[1])
        vector_abs = tuple(abs(x) for x in vector)
        print(vector_abs)
        if from_tile_object.piece != None:
            #if Piece of player
            if (from_tile_object.piece.name == "pawn"):
                print(vector, from_tile_object.piece.moves['w'])
                if vector in from_tile_object.piece.attacks and to_tile_object.piece != None and to_tile_object.piece.color != to_tile_object.piece.color:
                    print("pawn Attacks")
                    return True
                elif (from_tile_object.x == 7 or from_tile_object.x == 2) and (vector == (-2, 0) or vector == (2, 0)):
                    self.is_path_obstructed(from_tile_object.coords, to_tile_object.coords, vector)
                    print("pawn vector in first move")
                    return True
                elif (from_tile_object.piece.color == 'w') and (vector in from_tile_object.piece.moves['w']):
                    return True
                elif (from_tile_object.piece.color == 'b') and (vector in from_tile_object.piece.moves['b']):
                    return True
                else:
                    print("illegal")
                    return False
            else:
                if vector_abs in from_tile_object.piece.moves:
                    if from_tile_object.piece.name == "horseman":
                        if to_tile_object.piece == None or to_tile_object.piece.color != from_tile_object.piece.color:
                            return True
                        else:
                            print("it's your fucking piece dude")
                            return False
                    if self.is_path_obstructed(from_tile_object.coords, to_tile_object.coords, vector):
                        if to_tile_object.piece == None or to_tile_object.piece.color != from_tile_object.piece.color:
                            return True
                        else:
                            print("it's your fucking piece dude")
                            return False
                    else:
                        print("path obstructed")
                else:
                    print("illegal move")
                    return False
        else:
            print('????!')
            return False


    def get_tile_object(self, tile_coords):
        return next(tile for tile in self.tiles if tile.coords == tile_coords)

    def create_pieces(self):
        self.tiles[0].piece, self.tiles[7].piece, self.tiles[63].piece, self.tiles[56].piece = Tower("w"), Tower("w"), Tower("b"), Tower("b")
        self.tiles[1].piece, self.tiles[6].piece, self.tiles[62].piece, self.tiles[57].piece = Horseman("w"), Horseman("w"), Horseman("b"), Horseman("b")
        self.tiles[2].piece, self.tiles[5].piece, self.tiles[61].piece, self.tiles[58].piece = Bishop("w"), Bishop("w"), Bishop("b"), Bishop("b")
        self.tiles[3].piece, self.tiles[60].piece = Queen("w"), Queen("b")
        self.tiles[4].piece, self.tiles[59].piece = King("w"), King("b")
        for x in self.tiles[8:16]:
            x.piece = Pawn("w")
        for x in self.tiles[48:56]:
            x.piece = Pawn("b")


class Player:
    def __init__(self, connection):
        self.conn = connection
        self.id = uuid.uuid4().hex
        self.game = None

    def create_game(self):
        game = Game()
        self.game = game
        game.join(self)
        print(f"player {self} created game {game.id}")

    def join_game(self, game):
        game.join(self)
        print(f"player {self} joined game {game.id}")


class JoinGame(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        key = self.get_argument("id", None)
        response = {'gameId': key}
        print("client will be sent following information", response)
        new_player_join(response['gameId'])


class CreateGame(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        g = Game()
        g.board.create_pieces()
        print(f"Game with id {g.id} has been created")
        self.write(g.id)


class Controller(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = None
        self.get_player = None

    def get_player(self):
        self.player = next(player for player in self.game.players if player.conn == self)

    def check_origin(self, origin):
        return True

    def open(self):
        connList.append(self)

    def on_message(self, message):
        data = json.loads(message)
        if not self.game:
            self.game = next(x for x in gameList if x.id == data['gameId'])
        self.game.turn_of
        if data['option'] == 'join':
            p = Player(self)
            if len(gameList) > 0:
                if len(self.game.players) < 2:
                    self.game.join(p)
                    self.write_message(json.dumps({"state": "ready", "reason": "OK", "id": self.game.id}))
                else:
                    self.write_message(json.dumps({"state": "denied", "reason": "lobby full", "id": self.game.id}))
            else:
                self.write_message('no games are being played atm')
        elif data['option'] == 'refr':
            sendData(data, 'refr')

        if data['option'] == 'move':

            from_tile_coords = (int(data['move_data']['piece'][0]), int(data['move_data']['piece'][1]))
            to_tile_coords = (int(data['move_data']['to'][0]), int(data['move_data']['to'][1]))

            if self.game.board.validate_move(from_tile_coords, to_tile_coords):
                moving_piece = self.game.board.get_tile_object(from_tile_coords).piece
                self.game.board.get_tile_object(from_tile_coords).piece = None
                self.game.board.get_tile_object(to_tile_coords).piece = moving_piece
                print([(x.x, x.y, x.piece) for x in self.game.board.tiles])
                self.game.next_player()
                sendData(data, 'refr')
            else:
                sendData(data, 'refr')


def make_app():
    return tornado.web.Application([
        (r"/join_game", JoinGame),
        (r"/create_game", CreateGame),
        (r"/game", Controller),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    print(f"Listening localhost on {PORT}")
    tornado.ioloop.IOLoop.current().start()
