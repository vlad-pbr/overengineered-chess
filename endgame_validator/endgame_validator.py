#!/usr/bin/env python3.8

"""
Endgame validator receives message from move validator after a move
has been performed and checks if the game has ended. The move is then
logged to the game stream.
"""

import os
import logging
from redis import Redis
from chess_utils import ChessBoard, stream_key_from_id

logger = logging.getLogger(__name__)
redis = Redis(  host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=0,
                decode_responses=True)

ENDGAME_STREAM_NAME = os.getenv("ENDGAME_STREAM_NAME", "endgame")

def main():
    
    logger.info("awaiting notifications from move validator")

    while True:

        # read single endgame message
        move = redis.xread({ENDGAME_STREAM_NAME: 0}, count=1, block=0)
        message_ts = move[0][1][0][0]
        game_id = int(move[0][1][0][1]["game_id"])

        logger.info(f"received notification for end validation for game {game_id}")

        # get board of current game
        board = ChessBoard(game_id, redis)

        # TODO actually check if endgame
        finished = False

        # if endgame detected
        if finished:

            # mark game as finished
            redis.expire(stream_key_from_id(game_id), 60)

            # remove handled move from stream and add move to game
            logger.info("marking completion of event")
            redis.xdel(ENDGAME_STREAM_NAME, message_ts)

if __name__ == "__main__":
    main()