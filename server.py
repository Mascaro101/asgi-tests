from fastapi import FastAPI, WebSocket
from starlette.responses import FileResponse
import os
import random
import asyncio

app = FastAPI()

@app.get("/")
async def read_root():
    return FileResponse('/home/mascaro101/casino_asgi/templates/index.html')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()  # Receive a message from the client
        await websocket.send_text(data)  # Send the received message back to the client