import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

import { WebsocketService } from '../shared/services/websocket.service'
import { ENV } from '../shared/env'

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {

  log: string = ""
  game_id: number = 1
  is_white: boolean = true
  isNaN = isNaN

  constructor(private websocketService: WebsocketService, private router: Router, private http: HttpClient) { }

  ngOnInit(): void { }

  create(game_id: number) {

    // try creating game with given ID
    this.http.post(`${ENV.GATEWAY_HTTP_ENDPOINT}/game/${game_id}/create`, null).subscribe({
      complete: () => {
        this.join(game_id)
      },
      error: (e) => {
        this.log =(e as HttpErrorResponse).error
      }
    })

  }

  join(game_id: number) {

    this.log = "Connecting..."

    // connect to server
    this.websocketService.connect(`/game/${game_id}/join`, () => {

      // change view to actual game
      this.router.navigate([`/game/${game_id}`], {
        queryParams: {
          is_white: this.is_white
        }
      })

    }, () => {

      this.log = `Game with ID ${game_id} does not exist.`

    })

  }

  handle_id_change(e: Event): void {
    this.game_id = parseInt((e as InputEvent).data!)
  }

  handle_color_change(e: Event): void {
    this.is_white = (e.target as HTMLInputElement).value === "white"
  }

}
