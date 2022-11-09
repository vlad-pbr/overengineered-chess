import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';

import { range } from '../shared/utils'
import { GameEvent, EventType } from '../shared/models/gameevent.model'
import { Coordinate, is_coordinate_in, is_coordinate_equal } from '../shared/models/coordinate.model'
import { Move } from '../shared/models/move.model'
import { DEFAULT_CHESSBOARD } from '../shared/models/chesspiece.model'
import { WebsocketService } from '../shared/services/websocket.service'
import { ENV } from '../shared/env'

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css']
})
export class GameComponent implements OnInit {

  game_id: number
  turn_white: boolean = true
  is_white?: boolean = undefined
  focused_chesspiece?: Coordinate = undefined
  focused_spots: Coordinate[] = []
  board_locked: boolean = false
  chessboard = DEFAULT_CHESSBOARD
  log: string = ""
  connection_log: string = ""
  range = range

  constructor(private websocketService: WebsocketService, private route: ActivatedRoute, private http: HttpClient) {

    this.game_id = parseInt(this.route.snapshot.paramMap.get("game-id") as string)
    let is_white: string = this.route.snapshot.queryParams["is_white"]
    if (is_white != undefined) {
      this.is_white = is_white === 'true'
    }

  }

  ngOnInit(): void {

    if (this.check_conditions()) {

      const event_resolver: { [event: string]: (e: GameEvent) => void } = {
        [EventType.MOVE]: (e) => {

          // perform move on chessboard
          this.chessboard[e.move.dest_coordinate.y][e.move.dest_coordinate.x] = this.chessboard[e.move.src_coordinate.y][e.move.src_coordinate.x]
          this.chessboard[e.move.src_coordinate.y][e.move.src_coordinate.x] = undefined
          
          this.turn_white = !this.turn_white
          this.board_locked = false
        },
        [EventType.CHECK]: (e) => {
          this.log = "Check!"
        },
        [EventType.CHECKMATE]: (e) => {
          this.board_locked = true
          this.log = `Checkmate! ${this.turn_white ? 'White' : 'Black'} wins!`
        }
      }

      // subscribe to game moves and handle each move
      this.websocketService.get_events()?.subscribe({
        next: (e) => { this.log = ""; event_resolver[e.event](e) },
        complete: () => {
          this.connection_log = "(Game disconnected)"
        }
      })
    }

  }

  get_chessboard_spot_class(x: number, y: number): string {
    return `chessboard-${x % 2 != y % 2 ? "black" : "white"} `
      + `${this.focused_chesspiece && is_coordinate_equal({ x, y }, this.focused_chesspiece!) ? "focused-piece" : ""} `
      + `${is_coordinate_in({ x, y }, this.focused_spots) ? "focused-spot" : ""}`
  }

  check_conditions(): boolean {
    return !isNaN(this.game_id)
      && this.is_white != undefined
      && this.websocketService.connected()
  }

  handle_select(x: number, y: number): void {

    // make sure board is not locked and it's user's turn
    if (this.board_locked || this.is_white != this.turn_white) {
      return
    }

    // if a piece is already focused
    if (this.focused_chesspiece) {

      // additional click unfocuses the piece
      if (is_coordinate_equal({ x, y }, this.focused_chesspiece)) {
        this.unfocus()
      }

      // a click on one of the suggestions performs a move
      else if (is_coordinate_in({ x, y }, this.focused_spots)) {
        this.perform_move(this.focused_chesspiece, { x, y })
      }

      // if no piece is focused
    } else {

      // if player owns the chess piece - focus on it
      if (this.chessboard[y][x] && this.chessboard[y][x]!.is_white == this.is_white) {
        this.focus({ x, y })
      }

    }

  }

  focus(c: Coordinate): void {

    this.board_locked = true
    this.unfocus()

    // get all move suggestions and focus on them
    this.focused_chesspiece = c
    this.http.post<Coordinate[]>(`${ENV.GATEWAY_HTTP_ENDPOINT}/game/${this.game_id}/suggest`, c).subscribe({
      next: (suggestions) => {
        this.focused_spots = suggestions
      },
      complete: () => {
        this.board_locked = false
      }
    })

  }

  unfocus(): void {

    if (this.focused_chesspiece) {
      this.focused_chesspiece = undefined
      this.focused_spots = []
    }

  }

  perform_move(src: Coordinate, dest: Coordinate): void {

    // unfocus piece
    this.board_locked = true
    this.unfocus()

    // perform move
    let move: Move = { src_coordinate: src, dest_coordinate: dest }
    this.http.post(`${ENV.GATEWAY_HTTP_ENDPOINT}/game/${this.game_id}/move`, move).subscribe({})
  }

}
