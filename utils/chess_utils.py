#!/usr/bin/env python3.8

"""
Various utility functions and classes related to the
overengineered game of chess.
"""

import json
from enum import Enum
from typing import Literal
from pydantic import BaseModel, ValidationError
from redis import Redis

# list of all valid axis values
VALID_COORDINATE = tuple([*range(0, 8)])


class EventTypes(Enum):
    MOVE = "move"
    CHECK = "check"
    CHECKMATE = "checkmate"


class Coordinate(BaseModel):

    x: Literal[VALID_COORDINATE]  # pylance does not like this for some reason
    y: Literal[VALID_COORDINATE]

    @staticmethod
    def from_literals(x: Literal[VALID_COORDINATE], y: Literal[VALID_COORDINATE]) -> 'Coordinate':
        return Coordinate(**{"x": x, "y": y})


class Move(BaseModel):
    src_coordinate: Coordinate
    dest_coordinate: Coordinate


class GameEvent(BaseModel):
    pass


class MoveGameEvent(GameEvent):
    event: str = EventTypes.MOVE.value
    move: Move


class CheckGameEvent(GameEvent):
    event: str = EventTypes.CHECK.value


class CheckmateGameEvent(GameEvent):
    event: str = EventTypes.CHECKMATE.value


class ChessPiece():

    def __init__(self, is_white: bool) -> None:
        self.is_white = is_white


class Pawn(ChessPiece):

    first_move: bool = True

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:

        out = []

        # check forward moves
        for i in [1] + ([2] if self.first_move else []):

            # derive xy of current iteration
            try:
                c = Coordinate.from_literals(
                    coordinate.x, coordinate.y + (-i if self.is_white else i))
            except ValidationError:
                break

            # if any piece obstructs the move - not a valid move
            if board.get(c) == None:
                out.append(c)
            else:
                break

        # pawns capture diagonally, so diagonal moves are checked separately
        for i in [1, -1]:

            # derive xy of current iteration
            try:
                c = Coordinate.from_literals(
                    coordinate.x + i, coordinate.y + (-1 if self.is_white else 1))
            except ValidationError:
                continue

            piece = board.get(c)

            # if a chess piece exists and is of different color - capture
            if piece and piece.is_white != self.is_white:
                out.append(c)

        return out


class Rook(ChessPiece):

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:

        out = []

        for i in [(0, 1), (0, -1), (1, 0), (-1, 0)]:

            multiplier = 2

            try:

                c = Coordinate.from_literals(
                    coordinate.x + i[0], coordinate.y + i[1])
                piece = board.get(c)

                # while within borders
                while piece != False:

                    # if piece is encountered
                    if piece:

                        # if piece is of opposite color - capture
                        if piece.is_white != self.is_white:
                            out.append(c)

                        break

                    # empty spot
                    else:
                        out.append(c)

                    # advance
                    c = Coordinate.from_literals(
                        coordinate.x + (i[0] * multiplier), coordinate.y + (i[1] * multiplier))
                    multiplier += 1
                    piece = board.get(c)

            except ValidationError:
                continue

        return out


class Knight(ChessPiece):

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:

        out = []

        # iterate all possible knight offsets
        for i in [
            (-1, -2), (1, -2),
            (2, -1), (2, 1),
            (-1, 2), (1, 2),
            (-2, -1), (-2, 1)
        ]:

            try:
                c = Coordinate.from_literals(
                    coordinate.x + i[0], coordinate.y + i[1])
            except ValidationError:
                continue

            piece = board.get(c)

            # if empty space or opposite pawn - append
            if piece == None or (piece and piece.is_white != self.is_white):
                out.append(c)

        return out


class Bishop(ChessPiece):

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:

        out = []

        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:

            multiplier = 2

            try:

                c = Coordinate.from_literals(
                    coordinate.x + i[0], coordinate.y + i[1])
                piece = board.get(c)

                # while within borders
                while piece != False:

                    # if piece is encountered
                    if piece:

                        # if piece is of opposite color - capture
                        if piece.is_white != self.is_white:
                            out.append(c)

                        break

                    # empty spot
                    else:
                        out.append(c)

                    # advance
                    c = Coordinate.from_literals(
                        coordinate.x + (i[0] * multiplier), coordinate.y + (i[1] * multiplier))
                    multiplier += 1
                    piece = board.get(c)

            except ValidationError:
                continue

        return out


class Queen(ChessPiece):

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:

        return Rook(self.is_white).get_valid_moves(board, coordinate) \
            + Bishop(self.is_white).get_valid_moves(board, coordinate)


class King(ChessPiece):

    def get_valid_moves(self, board: 'ChessBoard', coordinate: Coordinate) -> list:

        out = []

        # iterate all possible king offsets
        for i in [
            (-1, -1), (0, -1),
            (1, -1), (1, 0),
            (1, 1), (0, 1),
            (-1, 1), (-1, 0)
        ]:

            try:
                c = Coordinate.from_literals(
                    coordinate.x + i[0], coordinate.y + i[1])
            except ValidationError:
                continue

            piece = board.get(c)

            # if empty space or opposite pawn - append
            if piece == None or (piece and piece.is_white != self.is_white):
                out.append(c)

        return out


class ChessBoard:

    """
    Represents chess pieces on a chess board.
    A board is initialized by reading game state from redis.
    Moves can then be performed on that board using move() 
    """

    def __init__(self, game_id: int, redis: Redis) -> None:

        # custom game move iterator, because why not
        class Game:

            def __init__(self, game_id: int, redis: Redis):
                self.redis = redis
                self.stream_key = stream_key_from_id(game_id)
                self.ts = 0

            def __iter__(self):
                return self

            def __next__(self) -> Move:

                while True:

                    # read next move from redis
                    move = redis.xread({self.stream_key: self.ts}, count=1)

                    if move:

                        # store timestamp and return parsed move
                        self.ts = move[0][1][0][0]
                        move_data = json.loads(move[0][1][0][1]["data"])

                        if move_data["event"] == EventTypes.MOVE.value:
                            return Move(**move_data["move"])

                    else:

                        raise StopIteration

        # init empty chess board matrix
        self._matrix = [[None for _ in range(0, 8)] for _ in range(0, 8)]

        # spawn pawns
        for y in [(1, False), (6, True)]:
            for x in range(0, 8):
                self._matrix[y[0]][x] = Pawn(y[1])

        # spawn rooks
        for y in [(0, False), (7, True)]:
            for x in [0, 7]:
                self._matrix[y[0]][x] = Rook(y[1])

        # spawn knights
        for y in [(0, False), (7, True)]:
            for x in [1, 6]:
                self._matrix[y[0]][x] = Knight(y[1])

        # spawn bishops
        for y in [(0, False), (7, True)]:
            for x in [2, 5]:
                self._matrix[y[0]][x] = Bishop(y[1])

        # spawn queens
        for y in [(0, False), (7, True)]:
            self._matrix[y[0]][3] = Queen(y[1])

        # spawn kings
        for y in [(0, False), (7, True)]:
            self._matrix[y[0]][4] = King(y[1])

        # add each move to chessboard
        self.history = []
        for move in Game(game_id, redis):
            self.move(move)

    def get(self, c: Coordinate):
        """
        Gets an element from the chess board.
        Returns ChessPiece if there is a chess price.
        Returns None if no chess piece.
        Returns False if coordinate out of bounds.
        """

        try:
            return self._matrix[c.y][c.x]
        except IndexError:
            return False

    def move(self, move: Move) -> bool:
        """
        Performs move on a chessboard.
        Returns True if successful, otherwise False.
        """

        piece = self.get(move.src_coordinate)

        # make sure source is a valid piece
        if not piece:
            return False

        # make sure the turn checks out
        if piece.is_white != self.is_white_turn():
            return False

        # make sure move itself is valid
        if move.dest_coordinate not in piece.get_valid_moves(self, move.src_coordinate):
            return False

        # move piece
        self._matrix[move.src_coordinate.y][move.src_coordinate.x] = None
        self._matrix[move.dest_coordinate.y][move.dest_coordinate.x] = piece

        self.history.append(move)

        if isinstance(piece, Pawn):
            piece.first_move = False

        return True

    def find_checks(self):
        """
        Searches for existing check or checkmate.
        Returns appropriate object if found.
        Returns None otherwise.
        """

        for y in range(0, 8):
            for x in range(0, 8):

                c = Coordinate.from_literals(x, y)
                piece = self.get(c)

                # if piece is found
                if piece:

                    # get it's valid moves
                    spots = piece.get_valid_moves(self, c)

                    for spot in spots:

                        # check if valid move is for an opposite king
                        target_piece = self.get(spot)

                        if target_piece \
                                and isinstance(target_piece, King) \
                                and piece.is_white != target_piece.is_white:

                            if self.is_white_turn() == target_piece.is_white:
                                return CheckGameEvent()
                            else:
                                return CheckmateGameEvent()

        return None

    def is_white_turn(self) -> bool:
        return len(self.history) % 2 == 0


def game_exists(game_id: int, redis: Redis) -> bool:
    """Checks existence of a related redis stream."""

    return redis.exists(stream_key_from_id(game_id)) != 0


def stream_key_from_id(id: int) -> str:
    """Outputs stream key by game id so all stream names follow the same format."""

    return f"game-{id}"


def write_event_to_game(game_id: int, redis: Redis, event: GameEvent):
    """Writes data to game stream."""

    redis.xadd(stream_key_from_id(game_id), {"data": json.dumps(event.dict())})
