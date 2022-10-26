#!/usr/bin/env python3.8

from fastapi import FastAPI, WebSocket, status

app = FastAPI()

@app.websocket("/game/{game_id}")
async def get_game(websocket: WebSocket, game_id: int):
    
    # await websocket.accept()

    # TODO while true, send game id moves to client 
    pass

@app.post("/game/{game_id}", status_code=status.HTTP_201_CREATED)
async def new_game(game_id: int):

    # TODO new redis stream
    pass

@app.post("/game/{game_id}/move", status_code=status.HTTP_201_CREATED)
def perform_move(game_id: int):

    # TODO query move-validator for validation
    pass

if __name__ == "__main__":
    pass