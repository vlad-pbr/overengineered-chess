import { Component, ComponentFactoryResolver, OnInit } from '@angular/core';
import { WebsocketService } from '../websocket.service'
import { Router } from '@angular/router';


@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {

  constructor(private websocketService: WebsocketService, private router: Router) { }

  log_error(message: string): void {
    (document.getElementById("error-log") as HTMLParagraphElement).textContent = message
  }

  play(action: string) {

    let game_id: number = this.get_id()

    // if socket connection is successful - redirect to game
    if (this.websocketService.connect(`/game/${game_id}/${action}`)) {
      this.router.navigate([`/game/${game_id}`], { 
        queryParams: { 
          is_white: action == "create" ? true : false
        }
      })
    } else {
      this.log_error("An error has occurred.")
    }

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
