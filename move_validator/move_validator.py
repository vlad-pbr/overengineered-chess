#!/usr/bin/env python3.8

"""
Move validator does exactly that, validate chess moves.
It builds game state out of performed moves and then decides if provided move
is valid. It then returns response to gateway and notifies endgame microservice
via redis stream.
"""

import os
from redis import Redis
from chess_utils import Move, ChessBoard, stream_key_from_id
from fastapi import FastAPI, Response, Body, status

redis = Redis(  host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=0,
                decode_responses=True)
app = FastAPI()

@app.post("/validate", status_code=status.HTTP_201_CREATED)
def validate_move(game_id: int, move: Move = Body()):

    """Makes sure provided move is valid. Notifies endgame validator."""

    # init new board
    board = ChessBoard()
    
    stream_key = stream_key_from_id(game_id)

    # TODO actually check the move

    # notify endgame validator
    redis.xadd(os.getenv("ENDGAME_STREAM_NAME", "endgame"), move.dict())
