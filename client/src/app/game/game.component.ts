import { Component, OnInit } from '@angular/core';
import { WebsocketService, Move } from '../websocket.service'
import { ActivatedRoute } from '@angular/router';

const CHESS_PIECES = {
  PAWN_WHITE: "pawn_white.png",
  PAWN_BLACK: "pawn_black.png",
  ROOK_WHITE: "rook_white.png",
  ROOK_BLACK: "rook_black.png",
  KNIGHT_WHITE: "knight_white.png",
  KNIGHT_BLACK: "knight_black.png",
  BISHOP_WHITE: "bishop_white.png",
  BISHOP_BLACK: "bishop_black.png",
  QUEEN_WHITE: "queen_white.png",
  QUEEN_BLACK: "queen_black.png",
  KING_WHITE: "king_white.png",
  KING_BLACK: "king_black.png"
}

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css']
})
export class GameComponent implements OnInit {

  chessboard_colors = {
    black: "#466d1d",
    white: "#98bf64"
  }

  game_id: number
  is_white?: boolean = undefined

  chessboard = [
    [
      CHESS_PIECES.ROOK_BLACK,
      CHESS_PIECES.KNIGHT_BLACK,
      CHESS_PIECES.BISHOP_BLACK,
      CHESS_PIECES.QUEEN_BLACK,
      CHESS_PIECES.KING_BLACK,
      CHESS_PIECES.BISHOP_BLACK,
      CHESS_PIECES.KNIGHT_BLACK,
      CHESS_PIECES.ROOK_BLACK
    ],
    [
      CHESS_PIECES.PAWN_BLACK,
      CHESS_PIECES.PAWN_BLACK,
      CHESS_PIECES.PAWN_BLACK,
      CHESS_PIECES.PAWN_BLACK,
      CHESS_PIECES.PAWN_BLACK,
      CHESS_PIECES.PAWN_BLACK,
      CHESS_PIECES.PAWN_BLACK,
      CHESS_PIECES.PAWN_BLACK
    ],
    [ null, null, null, null, null, null, null, null ],
    [ null, null, null, null, null, null, null, null ],
    [ null, null, null, null, null, null, null, null ],
    [ null, null, null, null, null, null, null, null ],
    [
      CHESS_PIECES.PAWN_WHITE,
      CHESS_PIECES.PAWN_WHITE,
      CHESS_PIECES.PAWN_WHITE,
      CHESS_PIECES.PAWN_WHITE,
      CHESS_PIECES.PAWN_WHITE,
      CHESS_PIECES.PAWN_WHITE,
      CHESS_PIECES.PAWN_WHITE,
      CHESS_PIECES.PAWN_WHITE
    ],
    [
      CHESS_PIECES.ROOK_WHITE,
      CHESS_PIECES.KNIGHT_WHITE,
      CHESS_PIECES.BISHOP_WHITE,
      CHESS_PIECES.QUEEN_WHITE,
      CHESS_PIECES.KING_WHITE,
      CHESS_PIECES.BISHOP_WHITE,
      CHESS_PIECES.KNIGHT_WHITE,
      CHESS_PIECES.ROOK_WHITE
    ]
  ]

  constructor(private websocketService: WebsocketService, private route: ActivatedRoute) { 

    // resolve params
    this.game_id = parseInt(this.route.snapshot.paramMap.get("game-id") as string)
    let is_white: string = this.route.snapshot.queryParams["is_white"]
    if (is_white != undefined) {
      this.is_white = is_white === 'true'
    }

    // make sure game conditions check out
    if (this.check_conditions()) {

      let handle_move = (m: Move) => {
        console.log(m)
        this.chessboard[m.dest_coordinate.y][m.dest_coordinate.x] = this.chessboard[m.src_coordinate.y][m.src_coordinate.x]
        this.chessboard[m.src_coordinate.y][m.src_coordinate.x] = null
      }

      // subscribe to game moves and handle each move
      websocketService.get_moves()?.subscribe({
        next(m) { handle_move(m) }
      })

    }

  }

  check_conditions(): boolean {
    return  !isNaN(this.game_id)
            && this.is_white != undefined
            && this.websocketService.connected()
  }

  ngOnInit(): void {
  }

}
