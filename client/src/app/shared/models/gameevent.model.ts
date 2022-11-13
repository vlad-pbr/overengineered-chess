import { Move } from './move.model'

export enum EventType {
    MOVE = "move",
    CHECK = "check",
    CHECKMATE = "checkmate"
}

export interface GameEvent {
    event: EventType
    move: Move
    white_wins: boolean
}