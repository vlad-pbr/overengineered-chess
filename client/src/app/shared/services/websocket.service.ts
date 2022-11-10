import { Injectable } from '@angular/core';
import { Observable, Observer } from 'rxjs';

import { GameEvent } from '../models/gameevent.model'
import { ENV } from '../env'

@Injectable()
export class WebsocketService {

  private observable?: Observable<GameEvent>
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

      this.ws!.onerror = null

      this.observable = new Observable((observer: Observer<GameEvent>) => {

        this.ws!.onmessage = (messageEvent: MessageEvent<any>) => {
          observer.next(JSON.parse(messageEvent.data) as GameEvent)
        }
        this.ws!.onclose = (closeEvent: CloseEvent) => {
          observer.complete()
          this.ws = undefined
        }
        this.ws!.onerror = (ev: Event) => {
          console.log(ev)
        }

      })

      success_callback()
    }
  }

  connected(): boolean {
    return !!this.ws
  }

  get_events(): Observable<GameEvent> | undefined {
    return this.connected() ? this.observable : undefined
  }
}
