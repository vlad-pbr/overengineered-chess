import { Component, ComponentFactoryResolver, OnInit } from '@angular/core';
import { WebsocketService } from '../websocket.service'
import { Router } from '@angular/router';


@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {

  actions = {
    create: "create",
    join: "join"
  }

  constructor(private websocketService: WebsocketService, private router: Router) { }

  log(message: string): void {
    (document.getElementById("log") as HTMLParagraphElement).textContent = message
  }

  play(action: string) {

    let game_id: number = this.get_id()

    this.log("Connecting...")

    // connect to server
    this.websocketService.connect(`/game/${game_id}/${action}`, () => {

      // change view to actual game
      this.router.navigate([`/game/${game_id}`], { 
        queryParams: { 
          is_white: action == this.actions.create ? true : false
        }
      })

    }, () => {

      // report connection errors
      if (action == this.actions.create) {
        this.log(`Game with ID ${game_id} already exists.`)
      } else {
        this.log(`Game with ID ${game_id} does not exist.`)
      }

    })

  }

  get_id(): number {
    return parseInt((document.getElementById("game-id") as HTMLInputElement).value)
  }

  handleIDchange(): void {

    // disable buttons on invalid game ID
    let buttons = document.getElementsByClassName("menu-button") as HTMLCollectionOf<HTMLButtonElement>
    for (let i = 0; i < buttons.length; i++) {
      buttons[i].disabled = isNaN(this.get_id()) ? true : false
    }

  }

  ngOnInit(): void {}

}
