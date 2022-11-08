import { Injectable } from '@angular/core';
import { Observable, Observer } from 'rxjs';

import { GameEvent } from '../models/gameevent.model'
import { ENV } from '../env'

@Injectable()
export class WebsocketService {

  private observable?: Observable<GameEvent> = undefined
  private ws?: WebSocket = undefined

  constructor() { }

  connect(uri: string, success_callback: Function, error_callback: Function): void {

    // connect to server
    this.ws = new WebSocket(`${ENV.GATEWAY_WS_ENDPOINT}${uri}`)

    // handle error during connection
    this.ws.onerror = () => {
      error_callback()
    }

    // store reference to ws
    let ws = this.ws

    // handle successful connection
    this.ws.onopen = () => {

      ws.onerror = null

      this.observable = new Observable((observer: Observer<GameEvent>) => {

        // handle new moves
        ws.onmessage = (messageEvent: MessageEvent<any>) => {
          observer.next(JSON.parse(messageEvent.data) as GameEvent)
        }

        // handle socket closure
        ws.onclose = (closeEvent: CloseEvent) => {
          observer.complete()
        }

        // handle errors
        ws.onerror = (ev: Event) => {
          console.log(ev)
        }

      })

      success_callback()

    }
  }

  connected(): boolean {
    return this.observable ? true : false
  }

  get_events(): Observable<GameEvent> | undefined {
    return this.connected() ? this.observable : undefined
  }
}
