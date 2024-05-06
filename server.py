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
        data = random.randint(0, 10)
        await websocket.send_text(f"Random number: {data}")
        await asyncio.sleep(1)