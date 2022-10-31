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
from chess_utils import Move, Coordinate, ChessBoard, stream_key_from_id
from redis import Redis
from fastapi import FastAPI, WebSocket, Response
from starlette.websockets import WebSocketState, WebSocketDisconnect
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

async def transmit_game(websocket: WebSocket, game_id: int):
    
    async def _update_websocket_state(websocket: WebSocket) -> bool:

        # websocket state is not automatically updated
        # therefore we simulate a check below
        # which triggers state change
        try:
            await asyncio.wait_for(
                websocket.receive_text(), 0.001
            )
        except asyncio.TimeoutError:
            pass

    # accept connection
    await websocket.accept()
    await asyncio.sleep(0)

    ts = 0
    stream_key = stream_key_from_id(game_id)

    try:

        # listen on stream and send new moves to client
        while True:

            # read move and timestamp
            move = redis.xread({stream_key: ts}, count=1, block=5000)

            # check websocket state
            await _update_websocket_state(websocket)
            if websocket.client_state != WebSocketState.CONNECTED:
                raise WebSocketDisconnect

            if move:

                # parse stream message
                ts = move[0][1][0][0]
                move_data = json.loads(move[0][1][0][1]["data"])

                # send move
                logger.info(f"[{websocket.client.host}:{websocket.client.port}] sending move for game id {game_id}: {move_data}")
                await websocket.send_json(move_data)
                await asyncio.sleep(0)

    except WebSocketDisconnect:
        pass

@app.websocket("/game/{game_id}/join")
async def join_game(websocket: WebSocket, game_id: int):
    
    """Simply sends game moves to client via websocket."""

    # make sure game exists
    stream_key = stream_key_from_id(game_id)
    if redis.exists(stream_key) == 0:
        return Response(status_code=status.WS_1008_POLICY_VIOLATION)

    # transmit moves
    await transmit_game(websocket, game_id)

@app.websocket("/game/{game_id}/create")
async def new_game(websocket: WebSocket, game_id: int):

    """
    Creates a new redis stream for given game id.
    Then transmits game moves via websocket.
    Finally deletes the redis stream on socket disconnect.
    """

    stream_key = stream_key_from_id(game_id)

    # make sure no duplicate game
    if redis.exists(stream_key) != 0:
        return Response(status_code=status.WS_1008_POLICY_VIOLATION)
    
    # create new stream
    #
    # NOTE: redis has seemingly no way of creating an empty stream
    # so we just create a stream with temp data and delete it
    ts = redis.xadd(stream_key, {"a":"b"})
    redis.xdel(stream_key, ts)
    logger.info(f"created game with id {game_id}")

    # transmit moves
    await transmit_game(websocket, game_id)

    # once socket has been disconnected - delete game
    logger.info(f"ending game with id {game_id}")
    redis.delete(stream_key)

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

@app.post("/game/{game_id}/suggest", status_code=status.HTTP_200_OK)
def suggest_move(game_id: int, coordinate: Coordinate = Body()):

    # make sure game exists
    stream_key = stream_key_from_id(game_id)
    if redis.exists(stream_key) == 0:
        logger.info(f"game id {game_id} not found")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # read current game
    board = ChessBoard(game_id, redis)
    piece = board.get(coordinate)

    # make sure chess piece exists on the board
    if not piece:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    return piece.get_valid_moves(board, coordinate)