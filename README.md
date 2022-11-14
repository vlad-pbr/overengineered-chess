Overengineered Chess
====================

Why? Because we can.

# Design

This app is comprised of the following parts:

- Client (Angular)
- Gateway (Python FastAPI)
- Redis (Redis)
- Move Validator (Python FastAPI)
- Endgame Validator (Python)

<p align="center">
  <img src="docs/diagram.png">
</p>

The following chapters explain how each moving part functions.

## Client

Angular client for the game. It lets user choose a color and create or join games using a game ID. It only communicates with the gateway.

It reads the following JSON file at `/usr/share/nginx/html/env.json`:

```json
{
    "GATEWAY_HTTP_ENDPOINT": "http://localhost:8000",
    "GATEWAY_WS_ENDPOINT": "ws://localhost:8000"
}
```

## Gateway

Gateway is the entity which sits between the user and the rest of the app. It's responsible for game management - creation of new games, state of the current games and addition of new moves.

It exposes the following API endpoints:

- `POST /game/{game_id}/create`: creates a Redis stream for a new game of chess where all events are stored
- `WS   /game/{game_id}/join`: establishes websocket connection through which game events will be transmitted to client
- `POST /game/{game_id}/move`: delegates new move to move validator for further validation and addition to the game stream
- `POST /game/{game_id}/suggest`: returns a list of valid moves for a given chess piece

It reads the following environment variables:

- `REDIS_HOST`: redis host to work with (default: `localhost`)
- `REDIS_PORT`: port to use when connecting to redis (default: `6379`)
- `MOVE_VALIDATOR_ENDPOINT`: endpoint to query for move validation (default: `http://localhost:8001`)

## Redis

The most quintessential deployment of Redis - single instance and non-persistent.

## Move Validator

Move validator does exactly that, validate chess moves. It builds game state out of performed moves and then decides if provided move is valid. It then returns response to gateway and notifies endgame microservice via redis stream.

It exposes the following API endpoints:

- `POST /validate`: makes sure provided move is valid, then notifies endgame validator and returns a success status code

It reads the following environment variables:

- `REDIS_HOST`: redis host to work with (default: `localhost`)
- `REDIS_PORT`: port to use when connecting to redis (default: `6379`)
- `ENDGAME_STREAM_NAME`: name for the redis stream to use to pass move notifications to endgame validator

## Endgame Validator

Endgame validator is a simple `while True` loop which listens on a Redis stream. It receives a message from move validator after a move has been performed and checks for existence of a check / checkmate. If a check is detected, it is logged to the game stream. If a checkmate is detected, it is logged and expiration of 60 seconds is set on the game stream.

It reads the following environment variables:

- `REDIS_HOST`: redis host to work with (default: `localhost`)
- `REDIS_PORT`: port to use when connecting to redis (default: `6379`)
- `ENDGAME_STREAM_NAME`: name for the redis stream to use to read move notifications from move validator
