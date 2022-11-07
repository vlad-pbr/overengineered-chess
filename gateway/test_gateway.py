#!/usr/bin/env python3.8

from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketState
from gateway import app, redis as app_redis
from redis import Redis
from chess_utils import Move, MoveGameEvent, Coordinate, game_exists, expire_game, init_game, write_event_to_game
from json import dumps

client = TestClient(app)
redis: Redis = app_redis


def test_create_game():

    # prepare vars
    game_id = 1
    request = {
        "url": f"/game/{game_id}/create",
        "data": dumps(Move(src_coordinate=Coordinate.from_literals(
            0, 6), dest_coordinate=Coordinate.from_literals(0, 4)).dict())
    }

    # make sure game does not exist yet
    assert not game_exists(game_id, redis)

    # assert successful creation returns 201
    assert client.post(**request).status_code == 201

    # assert game was created
    assert game_exists(game_id, redis)

    # assert 400 on duplicate game
    assert client.post(**request).status_code == 400

    # cleanup
    expire_game(game_id, redis, 0)
    assert not game_exists(game_id, redis)


def test_join_game():

    # init new game and make a move
    game_id = 1
    mge = MoveGameEvent(move=(Move(
        src_coordinate=Coordinate.from_literals(0, 6), dest_coordinate=Coordinate.from_literals(0, 4))))
    init_game(game_id, redis)
    write_event_to_game(game_id, redis, mge)

    # assert moves are being transmitted
    with client.websocket_connect(f"/game/{game_id}/join") as websocket:
        assert MoveGameEvent(**websocket.receive_json()) == mge
