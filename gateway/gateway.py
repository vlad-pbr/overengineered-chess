#!/usr/bin/env python3.8

"""
Gateway is the entity which sits between the user and the rest of the app.
It takes care of game management and delegates move validation to the
move validator microservice.
"""

import os
import asyncio
import requests
from requests.exceptions import RequestException
from chess_utils import Move, stream_key_from_id, parse_stream_output
from redis import Redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi import Body, status

redis = Redis(  host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=0,
                decode_responses=True)
app = FastAPI()

@app.websocket("/game/{game_id}")
async def get_game(websocket: WebSocket, game_id: int):
    
    """Sends game moves to client via websocket."""

    # make sure game exists
    stream_key = stream_key_from_id(game_id)
    if redis.exists(stream_key) == 0:
        return Response(status_code=status.WS_1008_POLICY_VIOLATION)

    await websocket.accept()

    # send existing moves to client
    moves = redis.xread({stream_key: 0})
    for move in parse_stream_output(moves):

        # schedule a message and sleep until completion
        await websocket.send_json(move)
        await asyncio.sleep(0)

    try:

        # listen on stream and send new moves to client
        while True:

            # block until new move is read, then send it
            moves = redis.xread({stream_key: "$"}, count=1, block=0)
            moves = parse_stream_output(moves)
            await websocket.send_json(moves[0])
            await asyncio.sleep(0)

    except WebSocketDisconnect:
        pass # connection is closed, nothing to do

@app.post("/game/{game_id}", status_code=status.HTTP_201_CREATED)
def new_game(game_id: int):

    """Creates a new redis stream for given game id."""

    stream_key = stream_key_from_id(game_id)

    # make sure no duplicate game
    if redis.exists(stream_key) != 0:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    # create new stream
    #
    # NOTE: redis has seemingly no way of creating an empty stream
    # so we just create a stream with temp data and delete it
    ts = redis.xadd(stream_key, {"a":"b"})
    redis.xdel(stream_key, ts)

@app.post("/move", status_code=status.HTTP_201_CREATED)
def perform_move(move: Move = Body()):

    # make sure game exists
    stream_key = stream_key_from_id(move.game_id)
    if redis.exists(stream_key) == 0:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:

        # post move to move validator
        response = requests.post(   os.getenv("MOVE_VALIDATOR_ENDPOINT", "http://localhost:8001/validate"),
                                    data=move.json(),
                                    timeout=0)

    except RequestException:
        return Response(status_code=status.HTTP_502_BAD_GATEWAY)

    # 400 from move validator - invalid move
    if response.status_code == 400:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
