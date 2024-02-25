from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from computer_vision.classification import get_clf_prediction

from PIL import Image
import numpy as np
import pybase64
import base64
import json
import cv2
import io

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_json(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return {200: "OK"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive()
            _, raw = data.get("text").split(",")


            img = Image.open(io.BytesIO(base64.b64decode(raw)))
            clf_prediction = get_clf_prediction(img)

           

            await manager.send_json(clf_prediction, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
