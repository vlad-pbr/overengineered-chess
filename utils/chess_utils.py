#!/usr/bin/env python3.8

from abc import ABC, abstractmethod
from typing import Literal
from xmlrpc.client import Boolean
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

class ChessPiece(ABC):

    def __init__(self, is_white: bool) -> None:
        super().__init__()
        self.is_white = is_white

    @staticmethod
    @abstractmethod
    def get_valid_moves(board: 'ChessBoard', coordinate: Literal[VALID_COORDINATES]) -> list:
        pass

class Pawn(ChessPiece):
    
    first_move: bool = True

    @staticmethod
    def get_valid_moves(board: 'ChessBoard', coordinate: Literal[VALID_COORDINATES]) -> list:
        pass

class Rook(ChessPiece):
    
    @staticmethod
    def get_valid_moves(board: 'ChessBoard', coordinate: Literal[VALID_COORDINATES]) -> list:
        pass

class Knight(ChessPiece):
    
    @staticmethod
    def get_valid_moves(board: 'ChessBoard', coordinate: Literal[VALID_COORDINATES]) -> list:
        pass

class Bishop(ChessPiece):
    
    @staticmethod
    def get_valid_moves(board: 'ChessBoard', coordinate: Literal[VALID_COORDINATES]) -> list:
        pass

class Queen(ChessPiece):
    
    @staticmethod
    def get_valid_moves(board: 'ChessBoard', coordinate: Literal[VALID_COORDINATES]) -> list:
        pass

class King(ChessPiece):
    
    @staticmethod
    def get_valid_moves(board: 'ChessBoard', coordinate: Literal[VALID_COORDINATES]) -> list:
        pass

class ChessBoard():

    def __init__(self) -> None:
        
        # init empty chess board matrix
        self.matrix = [[None]*8]*8

        # spawn pawns
        for y in [ (1, False), (6, True) ]:
            for x in range(1,9):
                self.matrix[y[0]][x] = Pawn(y[1])

        # spawn rooks
        for y in [ (0, False), (7, True) ]:
            for x in [ 0, 7 ]:
                self.matrix[y[0]][x] = Rook(y[1])

        # spawn knights
        for y in [ (0, False), (7, True) ]:
            for x in [ 1, 6 ]:
                self.matrix[y[0]][x] = Knight(y[1])

        # spawn bishops
        for y in [ (0, False), (7, True) ]:
            for x in [ 2, 5 ]:
                self.matrix[y[0]][x] = Bishop(y[1])

        # spawn queens
        for y in [ (0, False), (7, True) ]:
            self.matrix[y[0]][3] = Queen(y[1])

        # spawn kings
        for y in [ (0, False), (7, True) ]:
            self.matrix[y[0]][4] = King(y[1])

    def move(move: Move) -> bool:
        pass

def stream_key_from_id(id: int) -> str:

    """Outputs stream key by game id so all stream names follow the same format."""

    return f"game-{id}"
