#!/usr/bin/env python3.8

"""
Endgame validator receives message from move validator after a move
has been performed and checks if the game has ended. The move is then
logged to the game stream.
"""

import os
import logging
from redis import Redis
from chess_utils import stream_key_from_id

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
        move_ts = move[0][1][0][0]
        move_data = move[0][1][0][1]

        logger.info(f"received notification from endgame validator")

        # TODO actually check if endgame

        # remove handled move from stream and add move to game
        logger.info(f"adding move to move stream")
        redis.xdel(ENDGAME_STREAM_NAME, move_ts)
        redis.xadd( stream_key_from_id(move_data["game_id"]),
                    { k:v for k,v in move_data.items() if k != "game_id" })

if __name__ == "__main__":
    main()