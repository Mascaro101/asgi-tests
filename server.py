from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

import pymysql
import aiomysql
import asyncio

import secrets
import shortuuid
import json
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Access-Control-Allow-Origin configuration for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="/home/mascaro101/casino_asgi/templates")

async def get_db_connection():
    return await aiomysql.connect(host='mascaro101.mysql.pythonanywhere-services.com',
                                  user='mascaro101',
                                  password='laquegana123',
                                  db='mascaro101$CasinoDB',
                                  charset='utf8mb4',
                                  cursorclass=aiomysql.DictCursor)

async def get_player_one(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT player_1 FROM rooms WHERE room_id = %s", (room_id,))
            result = await cursor.fetchone()
            if result:
                return result['player_1']
            else:
                return "No room found with the given ID"
    finally:
        connection.close()

async def get_player_two(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT player_2 FROM rooms WHERE room_id = %s", (room_id,))
            result = await cursor.fetchone()
            if result:
                return result['player_2']
            else:
                return "No room found with the given ID"
    finally:
        connection.close()

async def create_rooms_table():
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id VARCHAR(100) PRIMARY KEY,
                    player_1 VARCHAR(100) NOT NULL,
                    player_2 VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await connection.commit()
    finally:
        connection.close()


@app.on_event("startup")
async def startup_event():
    await create_rooms_table()
    print("Database table setup completed.")

class Room(BaseModel):
    room_id: str
    player_1: str
    player_2: str = None

@app.post("/rooms/")
async def insert_room(room: Room, background_tasks: BackgroundTasks):
    background_tasks.add_task(insert_room_sync, room.room_id, room.player_1)
    return {"message": "Room creation initiated"}

async def insert_room_sync(room_id, player_1):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO rooms (room_id, player_1, player_2) VALUES (%s, %s, %s)",
                (room_id, player_1, "Waiting For Player 2")
            )
            await connection.commit()
    finally:
        connection.close()

@app.post("/join_session")
async def join_session(request: Request, background_tasks: BackgroundTasks, room_id: str = Form(...)):
    user = request.session.get("username")  # Safely getting the username to avoid KeyError
    room = room_id
    background_tasks.add_task(join_room_sync, room, user)

    # Construct the redirect URL
    redirect_url = f"/create_session/{room_id}"

    # Return a redirect response to the URL
    return RedirectResponse(url=redirect_url, status_code=303)  # Use 303 See Other for POST-to-GET redirect


async def join_room_sync(room_id: str, player_2: str):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE rooms SET player_2 = %s WHERE room_id = %s",
                (player_2, room_id)
            )
            await connection.commit()
    finally:
        connection.close()

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
async def create_session(request: Request, background_tasks: BackgroundTasks):
    room_id_gen = shortuuid.ShortUUID("23456789ABCDEF")
    room_id = room_id_gen.random(4)
    user = request.session["username"]
    request.session["room_id"] = room_id

    background_tasks.add_task(insert_room_sync, room_id, user)

    # Append the token to the URL
    redirect_url = f"/create_session/{room_id}"

    # Return a redirect response to the URL with the token
    return RedirectResponse(url=redirect_url)

@app.get("/create_session/{room_id}")
async def create_session_with_token(request: Request, room_id: str):
    # Render the create_session page with the token
    return templates.TemplateResponse("create_session.html", {"request": request, "room_id": room_id})

class User(BaseModel):
    username: str

@app.post("/set_username")
async def set_username(request: Request, user: User):
    username = user.username

    request.session.clear()

    request.session["username"] = username
    print(f"Username: {username}")

    return username

@app.websocket("/ws/{page}/{room_id}")
async def websocket_endpoint(websocket: WebSocket, page: str, room_id: str):
    await websocket.accept()
    try:
        if page == "create_room":
            while True:
                room = room_id
                player_1 = await get_player_one(room_id)
                player_2 = await get_player_two(room_id)

                data_to_send = json.dumps({"room": room, "player_1": player_1, "player_2": player_2})

                await websocket.send_text(data_to_send)

                # Pause for 2 seconds before the next iteration
                await asyncio.sleep(2)
        # Handle other pages...
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for room {room_id} on page {page}")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.close(code=1011, reason="Unexpected error")

