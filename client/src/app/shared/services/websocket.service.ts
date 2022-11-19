import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

import { GameEvent } from '../models/gameevent.model'
import { ENV } from '../env'

@Injectable()
export class WebsocketService {

  private game_events$ = new Subject<GameEvent>()
  private ws?: WebSocket

  constructor() { }

  connect(game_id: number, success_callback: Function, error_callback: Function): void {

    // connect to server
    this.ws = new WebSocket(`${ENV.GATEWAY_WS_ENDPOINT}/game/${game_id}/join`)

    // handle error during connection
    this.ws.onerror = (ev: Event) => {
      error_callback(ev)
    }

    // handle successful connection
    this.ws.onopen = () => {

      this.ws!.onmessage = (messageEvent: MessageEvent<any>) => {
        this.game_events$.next(JSON.parse(messageEvent.data) as GameEvent)
      }
      this.ws!.onclose = (closeEvent: CloseEvent) => {
        this.game_events$.complete()
        this.ws = undefined
      }
      this.ws!.onerror = (ev: Event) => {
        console.log(ev)
      }

      success_callback()
    }
  }

  connected(): boolean {
    return !!this.ws
  }

  get_events$(): Subject<GameEvent> {
    return this.game_events$
  }
}
