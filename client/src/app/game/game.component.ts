import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';

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
  locked: boolean = true
  chessboard = DEFAULT_CHESSBOARD
  colors = {
    black: "#466d1d",
    white: "#98bf64",
    focused_piece: "blue",
    focused_spot: "aqua"
  }

  constructor(private websocketService: WebsocketService, private route: ActivatedRoute, private http: HttpClient) {

    // resolve params
    this.game_id = parseInt(this.route.snapshot.paramMap.get("game-id") as string)
    let is_white: string = this.route.snapshot.queryParams["is_white"]
    if (is_white != undefined) {
      this.is_white = is_white === 'true'
    }

    // make sure game conditions check out
    if (this.check_conditions()) {

      let handle_event = (e: GameEvent) => {

        this.log("")

        // handle move event
        if (e.event === EventType.MOVE) {

          // perform move on chessboard
          this.chessboard[e.move.dest_coordinate.y][e.move.dest_coordinate.x] = this.chessboard[e.move.src_coordinate.y][e.move.src_coordinate.x]
          this.chessboard[e.move.src_coordinate.y][e.move.src_coordinate.x] = undefined

          // switch turns
          this.switch_turns()

          // unlock board
          this.set_lock(false)
        }

        // handle check
        else if (e.event === EventType.CHECK) {
          this.log("Check!")
        }

        // handle checkmate
        else if (e.event === EventType.CHECKMATE) {
          this.set_lock(true)
          this.log(`Checkmate! ${this.turn_white ? 'White' : 'Black'} wins!`)
        }
      }

      // subscribe to game moves and handle each move
      websocketService.get_events()?.subscribe({
        next: (e) => { handle_event(e) },
        complete: () => {
          (document.getElementById("connection-log") as HTMLParagraphElement).textContent = "(Game disconnected)"
        }
      })

      // unlock board
      this.set_lock(false)

    }

  }

  check_conditions(): boolean {
    return !isNaN(this.game_id)
      && this.is_white != undefined
      && this.websocketService.connected()
  }

  handle_select(x: number, y: number): void {

    // drop selections when board is locked
    if (this.locked) {
      return
    }

    // build coordinate out of X and Y
    let c: Coordinate = { x: x, y: y }

    // make sure it's user's turn
    if (this.is_white != this.turn_white) {
      return
    }

    // if a piece is already focused
    if (this.focused_chesspiece) {


      // additional click unfocuses the piece
      if (is_coordinate_equal(c, this.focused_chesspiece)) {

        this.unfocus()
      }

      // a click on one of the suggestions performs a move
      else if (is_coordinate_in(c, this.focused_spots)) {
        this.perform_move(this.focused_chesspiece, c)
      }

      // if no piece is focused
    } else {

      // if player owns the chess piece - focus on it
      if (this.chessboard[c.y][c.x]?.is_white == this.is_white) {

        this.focus(c)

      }

    }

  }

  focus(c: Coordinate): void {

    this.set_lock(true)

    // unfocus current piece
    if (this.focused_chesspiece) {
      this.unfocus()
    }

    // focus new piece
    this.focused_chesspiece = c
    this.set_border(c, this.colors.focused_piece, true)

    // get all move suggestions and focus on them
    this.http.post<Coordinate[]>(`${ENV.GATEWAY_HTTP_ENDPOINT}/game/${this.game_id}/suggest`, c).subscribe({
      next: (suggestions) => {
        suggestions.forEach((suggestion) => {
          this.focused_spots.push(suggestion)
          this.set_border(suggestion, this.colors.focused_spot, true)
        })

        this.set_lock(false)
      }
    })

  }

  unfocus(): void {

    if (this.focused_chesspiece) {
      
      // remove reference to focused chesspiece
      this.set_border(this.focused_chesspiece, this.colors.focused_piece, false)
      this.focused_chesspiece = undefined

      // remove borders from focused spots
      this.focused_spots.forEach((spot) => { this.set_border(spot, this.colors.focused_spot, false) })

      // empty list of focused spots
      this.focused_spots = []
    }

  }

  set_border(c: Coordinate, color: string, set: boolean) {

    // get element
    let chesspiece = document.getElementById(`chesspiece-${c.x}-${c.y}`) as HTMLDivElement

    // set border
    chesspiece.style.outlineStyle = "solid"
    chesspiece.style.outlineOffset = "-0.75vh"
    chesspiece.style.outlineColor = color
    chesspiece.style.outlineWidth = set ? chesspiece.style.outlineOffset.slice(1) : "0"

  }

  perform_move(src: Coordinate, dest: Coordinate): void {

    // unfocus piece
    this.set_lock(true)
    this.unfocus()

    // perform move
    let move: Move = { src_coordinate: src, dest_coordinate: dest }
    this.http.post(`${ENV.GATEWAY_HTTP_ENDPOINT}/game/${this.game_id}/move`, move).subscribe({})
  }

  switch_turns() {
    this.turn_white = !this.turn_white
  }

  set_lock(locked: boolean) {
    this.locked = locked
  }

  log(message: string) {
    (document.getElementById("log") as HTMLParagraphElement).textContent = message
  }

  ngOnInit(): void {
  }

}
