#!/usr/bin/env python3.8

"""
Gateway is the entity which sits between the user and the rest of the app.
It takes care of game management and delegates move validation to the
move validator microservice.
"""

import os
import asyncio
import requests
import logging
import json
from requests.exceptions import RequestException
from chess_utils import Move, stream_key_from_id
from redis import Redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi import Body, status
from fastapi.logger import logger as fastapi_logger

# logger setup
logger = logging.getLogger('gunicorn.error')
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logging.DEBUG)

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

    # accept connection
    await websocket.accept()
    logger.info(f"accepted WS connection from {websocket.client.host}:{websocket.client.port}")

    try:

        ts = 0

        # listen on stream and send new moves to client
        while True:

            # read move and timestamp
            logger.info(f"""[{websocket.client.host}:{websocket.client.port}] awaiting move for game id {game_id}""")
            move = redis.xread({stream_key: ts}, count=1, block=0)
            ts = move[0][1][0][0]
            move_data = json.loads(move[0][1][0][1]["data"])

            # send move
            logger.info(f"[{websocket.client.host}:{websocket.client.port}] sending move for game id {game_id}: {move_data}")
            await websocket.send_json(move_data)
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
    logger.info(f"created game with id {game_id}")

@app.post("/game/{game_id}/move", status_code=status.HTTP_201_CREATED)
def perform_move(game_id: int, move: Move = Body()):

    """Performs move by delegating to move validator."""

    # make sure game exists
    stream_key = stream_key_from_id(game_id)
    if redis.exists(stream_key) == 0:
        logger.info(f"game id {game_id} not found")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:

        logger.info(f"delegating game id {game_id} move validation for the following move: {move.dict()}")

        # post move to move validator
        response = requests.post(   os.getenv(
                                        "MOVE_VALIDATOR_ENDPOINT",
                                        f"http://localhost:8001/validate"),
                                    data=move.json(),
                                    params={ "game_id": game_id },
                                    timeout=10)

        # raise exception on server-side errors
        logger.debug(response.status_code)
        if response.status_code >= 500:
            response.raise_for_status()

    except RequestException as e:
        logger.warn(f"an error occurred while validating move for game id {game_id}: {e}")
        return Response(status_code=status.HTTP_502_BAD_GATEWAY)

    # 400 from move validator - invalid move
    if response.status_code == 400:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
