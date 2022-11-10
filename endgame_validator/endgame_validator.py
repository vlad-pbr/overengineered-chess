#!/usr/bin/env python3.8

"""
Endgame validator receives message from move validator after a move
has been performed and checks if the game has ended. In case
the game has indeed ended, game is marked as finished by
setting expiration time on the game key within redis.
"""

import os
import logging
from redis import Redis
from chess_utils import ChessBoard, CheckmateGameEvent, stream_key_from_id, game_exists, write_event_to_game, expire_game

logging.basicConfig(level=logging.DEBUG)
redis = Redis(host=os.getenv("REDIS_HOST", "localhost"),
              port=int(os.getenv("REDIS_PORT", "6379")),
              db=0,
              decode_responses=True)

ENDGAME_STREAM_NAME = os.getenv("ENDGAME_STREAM_NAME", "endgame")


def main():

    logging.info("awaiting notifications from move validator")

    while True:

        # read single endgame message
        move = redis.xread({ENDGAME_STREAM_NAME: 0}, count=1, block=0)
        message_ts = move[0][1][0][0]
        game_id = int(move[0][1][0][1]["game_id"])

        logging.info(
            f"received notification for end validation for game {game_id}")

        if not game_exists(game_id, redis):
            logging.warn(
                f"received message for non-existing game (id {game_id})")

        else:

            # get board of current game
            event = ChessBoard.from_redis(game_id, redis).find_checks()

            # if check detected
            if event:

                # if checkmate - mark game as finished
                if isinstance(event, CheckmateGameEvent):
                    expire_game(game_id, redis, 60)

                # write event to game
                write_event_to_game(game_id, redis, event)

                # remove handled move from stream and add move to game
                logging.info(f"game id {game_id}: new event: {event}")

        redis.xdel(ENDGAME_STREAM_NAME, message_ts)


if __name__ == "__main__":
    main()
