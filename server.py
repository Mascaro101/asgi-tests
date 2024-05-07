from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
import secrets
import os
import random
import asyncio
import shortuuid
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

templates = Jinja2Templates(directory="/home/mascaro101/casino_asgi/templates")

@app.get("/")
async def read_root():
    return FileResponse('/home/mascaro101/casino_asgi/templates/index.html')


@app.get("/session_menu", response_class=HTMLResponse)
async def session_menu(request: Request):

    username = request.session.get("username", "Guest")

    print(request.session)

    print(username)
    return templates.TemplateResponse("session_menu.html", {"request": request, "USERNAME": username})


@app.get("/create_session")
async def create_session(request: Request):
    token = secrets.token_urlsafe(16)
    # Append the token to the URL
    redirect_url = f"/create_session/{token}"

    # Return a redirect response to the URL with the token
    return RedirectResponse(url=redirect_url)

@app.get("/create_session/{token}")
async def create_session_with_token(request: Request, token: str):
    # Render the create_session page with the token
    return templates.TemplateResponse("create_session.html", {"request": request, "token": token})

class User(BaseModel):
    username: str

@app.post("/set_username")
async def set_username(request: Request, user: User):
    username = user.username
    request.session["username"] = username

    print(f"Username: {username}")
    print(request.session["username"])
    return username

@app.websocket("/ws/{page}")
async def websocket_endpoint(websocket: WebSocket, page:str):
    await websocket.accept()
    # Generate a random number
    if page == "create_room":
        room_id_gen = shortuuid.ShortUUID("23456789ABCDEF")
        room_id = room_id_gen.random(4)
        # Convert the number to a string and send it to the client
        await websocket.send_text(str(room_id))
