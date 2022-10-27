#!/usr/bin/env python3.8

from typing import Literal
from pydantic import BaseModel

# list of all valid coordinates (a1 through h8)
VALID_COORDINATES = tuple(  [ f"{c}{i}" 
                            for c in 
                                [ chr(_c) for _c in range(ord('a'), ord('i')) ]
                            for i in 
                                [ *range(1,9) ]
                            ]) # no idea how to line break this properly

class Move(BaseModel):
    game_id: int
    src_coordinate: Literal[VALID_COORDINATES] # pylance does not like this for some reason
    dest_coordinate: Literal[VALID_COORDINATES]

def stream_key_from_id(id: int):

    """Outputs stream key by game id so all stream names follow the same format."""

    return f"game-{id}"
