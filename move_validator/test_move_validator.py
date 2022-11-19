#!/usr/bin/env python3.8

from fastapi.testclient import TestClient
from move_validator import app, redis as app_redis
from chess_utils import Move, Coordinate, init_game, game_exists
from redis import Redis
from json import dumps

client = TestClient(app)
redis: Redis = app_redis


def test_validate():

    # prepare vars
    game_id = 1
    request = {
        "url": "/validate",
        "data": dumps(Move(src_coordinate=Coordinate(
            x=0, y=6), dest_coordinate=Coordinate(x=0, y=4)).dict()),
        "params": {"game_id": game_id}
    }

    # assert non-existing game returns 400
    assert client.post(**request).status_code == 400

    # init new game
    init_game(game_id, redis)
    assert game_exists(game_id, redis)

    # assert valid move returns 201
    assert client.post(**request).status_code == 201

    # assert invalid move returns 400
    assert client.post(**request).status_code == 400
