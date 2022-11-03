import { Injectable } from '@angular/core';
import { UntypedFormBuilder } from '@angular/forms';
import { Observable, Observer } from 'rxjs';

interface Coordinate {
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

  private observable: Observable<Move> | undefined = undefined

  constructor() { }

  connect(uri: string): boolean {

    this.observable = new Observable((observer: Observer<Move>) => {

      // const ws = new WebSocket("ws://localhost:8000" + uri)

      // // handle new moves
      // ws.onmessage = (messageEvent: MessageEvent<any>) => {
      //   observer.next(messageEvent.data)
      // }

      // ws.onclose = (closeEvent: CloseEvent) => {
      //   observer.complete()
      // }

      // ======

      // temp test data
      observer.next( JSON.parse('{ "src_coordinate": { "x": 0, "y": 1 }, "dest_coordinate": { "x": 0, "y": 2 } }') as Move )
      observer.next( JSON.parse('{ "src_coordinate": { "x": 1, "y": 6 }, "dest_coordinate": { "x": 1, "y": 5 } }') as Move )
      observer.complete()

    } )

    return true
  }

  connected(): boolean {
    return this.observable ? true : false
  }

  get_moves(): Observable<Move> | undefined {
    return this.connected() ? this.observable : undefined
  }
}
