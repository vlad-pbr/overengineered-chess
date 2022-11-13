import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';

import { range } from '../shared/utils'
import { GameEvent, EventType } from '../shared/models/gameevent.model'
import { Coordinate, is_coordinate_in, is_coordinate_equal } from '../shared/models/coordinate.model'
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
  is_white?: boolean
  chessboard = DEFAULT_CHESSBOARD
  log: string = ""
  connection_log: string = "Connecting..."
  connection_error: string = ""
  init_complete: boolean = false
  init_timeout_id?: NodeJS.Timeout
  range = range
  private focused_chesspiece?: Coordinate
  private focused_spots: Coordinate[] = []
  private board_locked: boolean = false

  constructor(private websocketService: WebsocketService, private route: ActivatedRoute, private http: HttpClient) {

    this.game_id = parseInt(this.route.snapshot.queryParams["game_id"])
    const is_white: string = this.route.snapshot.queryParams["is_white"]
    if (is_white != undefined) {
      this.is_white = is_white === 'true'
    }

  }

  ngOnInit(): void {

    if (this.check_params()) {

      const setup = () => {

        const handle_init_timeout = (): NodeJS.Timeout => {
          if (this.init_timeout_id) {
            clearTimeout(this.init_timeout_id)
          }
          return setTimeout(() => { this.init_complete = true }, 1000)
        }
        this.init_timeout_id = handle_init_timeout()

        const event_resolver: { [event: string]: (e: GameEvent) => void } = {
          [EventType.MOVE]: (e) => {

            // perform move on chessboard
            this.chessboard[e.move.dest_coordinate.y][e.move.dest_coordinate.x] = this.chessboard[e.move.src_coordinate.y][e.move.src_coordinate.x]
            this.chessboard[e.move.src_coordinate.y][e.move.src_coordinate.x] = undefined

            this.turn_white = !this.turn_white
            this.board_locked = false

            // component is not rendered until init_complete is true
            // if 1s passes since the last move received - render the component
            if (!this.init_complete) {
              this.init_timeout_id = handle_init_timeout()
            }
          },
          [EventType.CHECK]: (e) => {
            this.log = "Check!"
          },
          [EventType.CHECKMATE]: (e) => {
            this.board_locked = true
            this.log = `Checkmate! ${!this.turn_white ? 'White' : 'Black'} wins!`
          }
        }

        // subscribe to game moves and handle each move
        this.websocketService.get_events$().subscribe({
          next: (e) => { this.log = ""; event_resolver[e.event](e) },
          complete: () => {
            this.connection_log = "game ended"
          }
        })

      }

      if (!this.websocketService.connected()) {
        this.websocketService.connect(this.game_id, setup, () => {
          this.connection_error = "game does not exist"
        })
      } else {
        setup()
      }
    }
  }

  is_connected(): boolean {
    return this.websocketService.connected()
  }

  get_chessboard_spot_class(x: number, y: number): string {
    return `chessboard-${x % 2 != y % 2 ? "black" : "white"} `
      + `${this.focused_chesspiece && is_coordinate_equal({ x, y }, this.focused_chesspiece!) ? "focused-piece" : ""} `
      + `${is_coordinate_in({ x, y }, this.focused_spots) ? "focused-spot" : ""}`
  }

  check_params(): boolean {
    return !isNaN(this.game_id)
      && this.is_white != undefined
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
      if (this.chessboard[y][x] && this.chessboard[y][x]!.is_white === this.is_white) {
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
    this.http.post(`${ENV.GATEWAY_HTTP_ENDPOINT}/game/${this.game_id}/move`,
      { src_coordinate: src, dest_coordinate: dest }).subscribe()
  }

}
