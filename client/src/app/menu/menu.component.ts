import { Component, ComponentFactoryResolver, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

import { WebsocketService } from '../websocket.service'
import { ENV } from '../env'

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {

  constructor(private websocketService: WebsocketService, private router: Router, private http: HttpClient) { }

  log(message: string): void {
    (document.getElementById("log") as HTMLParagraphElement).textContent = message
  }

  create(game_id: number) {

    // try creating game with given ID
    this.http.post(`http://${ENV.GATEWAY_ENDPOINT}/game/${game_id}/create`, null).subscribe({
      complete: () => {
        this.join(game_id)
      },
      error: (e) => {
        this.log((e as HttpErrorResponse).error)
      }
    })

  }

  join(game_id: number) {

    this.log("Connecting...")

    // connect to server
    this.websocketService.connect(`/game/${game_id}/join`, () => {

      // change view to actual game
      this.router.navigate([`/game/${game_id}`], {
        queryParams: {
          is_white: this.white_chosen()
        }
      })

    }, () => {

      this.log(`Game with ID ${game_id} does not exist.`)

    })

  }

  get_id(): number {
    return parseInt((document.getElementById("game-id") as HTMLInputElement).value)
  }

  white_chosen(): boolean {
    return (document.querySelector("input[name=color]:checked") as HTMLInputElement).value === "white"
  }

  handleIDchange(): void {

    // disable buttons on invalid game ID
    let buttons = document.getElementsByClassName("menu-button") as HTMLCollectionOf<HTMLButtonElement>
    for (let i = 0; i < buttons.length; i++) {
      buttons[i].disabled = isNaN(this.get_id()) ? true : false
    }

  }

  ngOnInit(): void { }

}
