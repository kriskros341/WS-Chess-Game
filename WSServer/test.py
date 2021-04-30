from chess import *


def test_p():
    p = Player(None)
    p.create_game()
    id = p.game.id
    new_player_join(id)
    print(p)
    print(p.game)
test_p()