#!/usr/bin/env python3.8

"""
Move validator does exactly that, validate chess moves.
It builds game state out of performed moves and then decides if provided move
is valid. It then returns response to gateway and notifies endgame microservice
via redis stream.
"""

import os
import logging
import json
from redis import Redis
from chess_utils import Move, ChessBoard, EventTypes, stream_key_from_id, game_exists
from fastapi import FastAPI, Response, Body, status
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

@app.post("/validate", status_code=status.HTTP_201_CREATED)
def validate_move(game_id: int, move: Move = Body()):

    """Makes sure provided move is valid. Notifies endgame validator."""

    logger.info(f"validating move for game id {game_id}: {move}")

    # make sure game exists
    if not game_exists(game_id, redis):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # init board for given game
    board = ChessBoard(game_id, redis)

    # check if move is valid
    if not board.move(move):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # append move to game
    logger.info(f"appending valid move to game id {game_id}: {move}")
    redis.xadd(stream_key_from_id(game_id), { "data": json.dumps({ "event": EventTypes.MOVE.value, "move": move.dict() }) } )

    # notify endgame validator
    logger.info(f"sending game id {game_id} move notification to endgame validator")
    redis.xadd(os.getenv("ENDGAME_STREAM_NAME", "endgame"), { "game_id": game_id } )
