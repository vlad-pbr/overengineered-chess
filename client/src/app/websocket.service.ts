import { Injectable } from '@angular/core';
import { Observable, Observer } from 'rxjs';

export interface Coordinate {
  x: number
  y: number
}

export interface Move {
  src_coordinate: Coordinate
  dest_coordinate: Coordinate
}

@Injectable({
  providedIn: 'root'
})
export class WebsocketService { 

  private observable?: Observable<Move> = undefined
  private ws?: WebSocket = undefined
  private close_code?: number = undefined

  constructor() { }

  connect(uri: string, success_callback: Function, error_callback: Function): void {

    // connect to server
    this.ws = new WebSocket("ws://localhost:8000" + uri)

    // handle error during connection
    this.ws.onerror = () => {
      error_callback()
    }

    // store reference to ws
    let ws = this.ws

    // handle successful connection
    this.ws.onopen = () => {

      ws.onerror = null

      this.observable = new Observable((observer: Observer<Move>) => {

        // handle new moves
        ws.onmessage = (messageEvent: MessageEvent<any>) => {
          observer.next(JSON.parse(messageEvent.data) as Move)
        }

        // handle socket closure
        ws.onclose = (closeEvent: CloseEvent) => {

          console.log(closeEvent)
          this.close_code = closeEvent.code
          observer.complete()
        }

        // handle errors
        ws.onerror = (ev: Event) => {
          console.log(ev)
        }

      } )

      success_callback()

    }
  }

  connected(): boolean {
    return this.observable ? true : false
  }

  get_moves(): Observable<Move> | undefined {
    return this.connected() ? this.observable : undefined
  }

  get_close_code(): number | undefined {
    return this.close_code
  }
}