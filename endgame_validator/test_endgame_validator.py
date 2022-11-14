#!/usr/bin/env python3.8

import json
from multiprocessing import Process
from endgame_validator import redis as app_redis, main as app_main
from redis import Redis
from chess_utils import write_event_to_game, stream_key_from_id, MoveGameEvent, Move, Coordinate, EventTypes

redis: Redis = app_redis

def test_checkmate():

    # prepare vars
    game_id = 1
    ts = 0

    # run endgame validator in a separate process
    app_process = Process(target=app_main)
    app_process.start()

    # set-up a checkmate
    for c in [
        ( Coordinate(x=5, y=6), Coordinate(x=5, y=5) ),
        ( Coordinate(x=4, y=1), Coordinate(x=4, y=3) ),
        ( Coordinate(x=6, y=6), Coordinate(x=6, y=4) ),
        ( Coordinate(x=3, y=0), Coordinate(x=7, y=4) ),
    ]:
        # write event to game and read it back
        write_event_to_game(game_id, redis, MoveGameEvent(move=Move(
            src_coordinate=c[0],
            dest_coordinate=c[1]
        )))
        redis.xadd("endgame", {"game_id": game_id})
        event = redis.xread({stream_key_from_id(game_id): ts}, count=1, block=0)
        ts = event[0][1][0][0]

    # read additional event and assert that it's a checkmate event
    event = redis.xread({stream_key_from_id(game_id): ts}, count=1, block=5000)
    try:
        assert json.loads(event[0][1][0][1]["data"])["event"] == EventTypes.CHECKMATE.value
    except KeyError:
        assert False

    app_process.terminate()