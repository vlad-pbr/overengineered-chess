#!/usr/bin/env python3.8

from abc import ABC, abstractmethod
from typing import Literal
from pydantic import BaseModel

# list of all valid axis values
VALID_COORDINATE = tuple([*range(0,8)])

class Coordinate(BaseModel):

    x: Literal[VALID_COORDINATE]
    y: Literal[VALID_COORDINATE]

    def __init__(self, x: Literal[VALID_COORDINATE], y: Literal[VALID_COORDINATE]) -> None:
        self.x = x
        self.y = y

class Move(BaseModel):
    src_coordinate: Coordinate # pylance does not like this for some reason
    dest_coordinate: Coordinate

class ChessPiece(ABC):

    def __init__(self, is_white: bool) -> None:
        super().__init__()
        self.is_white = is_white

    @abstractmethod
    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:
        pass

class Pawn(ChessPiece):
    
    first_move: bool = True

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:
        
        out = []

        # check forward moves
        for i in [1] + ([2] if self.first_move else []):

            # derive xy of current iteration
            c = Coordinate(coordinate.x, coordinate.y + (-i if self.is_white else i))

            # if any piece obstructs the move - not a valid move
            if board.get(c) == None:
                out.append(c)
            else:
                break

        # pawns capture diagonally, so diagonal moves are checked separately
        for i in [1, -1]:

            # derive xy of current iteration
            c = Coordinate(coordinate.x + i, coordinate.y + (-1 if self.is_white else 1))

            piece = board.get(c.x, c.y)

            # if a chess piece exists and is of different color - capture
            if piece and ChessPiece(piece).is_white != self.is_white:
                out.append(c)

        return out

class Rook(ChessPiece):
    
    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:
        
        out = []

        for i in [ (0,1), (0,-1), (1,0), (-1,0) ]:

            c = Coordinate(coordinate.x + i[0], coordinate.y + i[1])
            piece = board.get(c)

            # while within borders
            while piece != False:

                # if piece is encountered
                if piece:

                    # if piece is of opposite color - capture
                    if ChessPiece(piece).is_white != self.is_white:
                        out.append(c)

                    break

                # empty spot
                else:
                    out.append(c)

                # advance
                c.x += i[0]
                c.y += i[1]
                piece = board.get(c)

        return out

class Knight(ChessPiece):
    
    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:
        pass

class Bishop(ChessPiece):

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:
        pass

class Queen(ChessPiece):
    
    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:
        pass

class King(ChessPiece):
    
    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:
        pass

class ChessBoard():

    def __init__(self) -> None:
        
        # init empty chess board matrix
        self._matrix = [[None]*8]*8

        # spawn pawns
        for y in [ (1, False), (6, True) ]:
            for x in range(1,9):
                self._matrix[y[0]][x] = Pawn(y[1])

        # spawn rooks
        for y in [ (0, False), (7, True) ]:
            for x in [ 0, 7 ]:
                self._matrix[y[0]][x] = Rook(y[1])

        # spawn knights
        for y in [ (0, False), (7, True) ]:
            for x in [ 1, 6 ]:
                self._matrix[y[0]][x] = Knight(y[1])

        # spawn bishops
        for y in [ (0, False), (7, True) ]:
            for x in [ 2, 5 ]:
                self._matrix[y[0]][x] = Bishop(y[1])

        # spawn queens
        for y in [ (0, False), (7, True) ]:
            self._matrix[y[0]][3] = Queen(y[1])

        # spawn kings
        for y in [ (0, False), (7, True) ]:
            self._matrix[y[0]][4] = King(y[1])

    def get(self, c: Coordinate):

        """
        Gets an element from the chess board.
        Returns ChessPiece if there is a chess price.
        Returns None is no chess piece.
        Returns False if coordinate out of bounds.
        """

        try:
            return self._matrix[c.y][c.x]
        except IndexError:
            return False

    def move(self, move: Move) -> bool:

        piece = self.get(move.src_coordinate)

        # make sure source is a valid piece
        if not piece:
            return False

        piece = ChessPiece(piece)

        # make sure move itself is valid
        if move.dest_coordinate not in piece.get_valid_moves(self, move.src_coordinate):
            return False

        # move piece
        self._matrix[move.src_coordinate.y][move.src_coordinate.x] = None
        self._matrix[move.dest_coordinate.y][move.dest_coordinate.x] = piece

        return True

def stream_key_from_id(id: int) -> str:

    """Outputs stream key by game id so all stream names follow the same format."""

    return f"game-{id}"
