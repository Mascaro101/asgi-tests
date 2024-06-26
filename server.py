from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, BackgroundTasks, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

import asyncio
import random
from random import randint
import traceback
import shortuuid
import json

from db import (create_rooms_table, create_room_moves_table,
                insert_room_sync, join_room_sync, insert_room_move,
                get_player_one, get_player_two, have_both_moved, create_bingo_rooms_table,
                insert_bingo_room_sync, get_bingo_player_one, get_bingo_player_two,
                join_bingo_room_sync, is_room_active, insert_bingo_number, set_room_active, get_bingo_number,
                increment_bingo_pull_count, get_bingo_pull_count, reset_pull_count, create_bingo_history, insert_bingo_number_history, check_bingo_number)


from pydantic import BaseModel

# Initialize the FastAPI app with middleware for sessions
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Access-Control-Allow-Origin configuration for CORS
# Configured to allow cookies to be used in cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML file templates directory
templates = Jinja2Templates(directory="/home/mascaro101/casino_asgi/templates")

# Function to determine the winner of the game
async def rock_paper_scissors(room_id):
    ready, raw_result_player_1, raw_result_player_2 = await have_both_moved(room_id)

    if ready == True:
        result_player_1 = raw_result_player_1["player_1_moves"]
        result_player_2 = raw_result_player_2["player_2_moves"]

        ## ADD LOGIC FOR A ROCK PAPER SCISSORS GAME pereza

# Event on Startup
# Create the database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        await create_bingo_history()
        await create_rooms_table()
        await create_room_moves_table()
        await create_bingo_rooms_table()

        print("Database table setup completed.")
    except Exception as e:
        print(f"Failed to complete startup event: {e}")

# Room BaseModel Class
class Room(BaseModel):
    room_id: str
    player_1: str
    player_2: str = None

# User BaseModel Class
class User(BaseModel):
    username: str

# Join_Session Route
@app.post("/join_session")
async def join_session(request: Request, background_tasks: BackgroundTasks, room_id: str = Form(...)):

    # Get the username from the HTTP cookie and join the room
    user = request.session.get("username")
    room = room_id
    background_tasks.add_task(join_room_sync, room, user)

    # Construct the redirect URL
    redirect_url = f"/create_session/{room_id}"

    # Return a redirect response to the URL
    return RedirectResponse(url=redirect_url, status_code=303)

# Root Route
@app.get("/")
async def read_root():
    return FileResponse('/home/mascaro101/casino_asgi/templates/login_page.html')

# Session_Menu Route
@app.get("/session_menu", response_class=HTMLResponse)
async def session_menu(request: Request):

    # Get the username from the HTTP cookie
    username = request.session.get("username", "Guest")

    # Render the session_menu template with the username entered before
    return templates.TemplateResponse("session_menu.html", {"request": request, "USERNAME": username})

# Main Menu Route
@app.get("/main", response_class=HTMLResponse)
async def main_menu(request: Request):
    username = request.session.get("username", "None")

    return templates.TemplateResponse("main.html", {"request": request, "username": username})

# Create_Session Route
@app.get("/create_session")
async def create_session(request: Request, background_tasks: BackgroundTasks):
    ## If room is created after another user has been created in the same browser player1 = player2 -- ERROR

   # Generate a random room ID from ShortUUID
    room_id_gen = shortuuid.ShortUUID("23456789ABCDEF")
    room_id = room_id_gen.random(4)

    # Get the username and Save the room_id to the HTTP cookie
    user = request.session["username"]
    request.session["room_id"] = room_id

    # Create the room with the room_id and the Host
    background_tasks.add_task(insert_room_sync, room_id, user)

    # Append the token to the URL and redirect to the create_session page
    redirect_url = f"/create_session/{room_id}"
    return RedirectResponse(url=redirect_url)

# Create_Session with Token Route redirect
@app.get("/create_session/{room_id}")
async def create_session_with_token(request: Request, room_id: str):
    # Render the create_session page with the token
    return templates.TemplateResponse("create_session.html", {"request": request, "room_id": room_id})

# Set_Username Route
@app.post("/set_username")
async def set_username(request: Request, user: User):

    # Clear and save the username to the HTTP cookie
    username = user.username
    request.session.clear()
    request.session["username"] = username

    # Debug print the username
    print(f"Username: {username}")
    return username

# Serve static files
app.mount("/static", StaticFiles(directory="/home/mascaro101/casino_asgi/templates/static"), name="static")

# Bingo game route
@app.get("/tragaperras")
async def tragaperras(request: Request):
    return templates.TemplateResponse("tragaperras.html", {"request": request})

# Bingo game route
@app.get("/bingo")
async def bingo(request: Request):
    request.session["bingo_numbers"] = []
    return templates.TemplateResponse("bingo.html", {"request": request})

@app.post("/generate_bingo_number")
def generate_number(request: Request):
    used_numbers = request.session["bingo_numbers"]
    number = random.randint(0, 100)

    while number in used_numbers:
        number = random.randint(0, 100)

    used_numbers.append(number)
    return {"number": number}

@app.post("/generate_next_number")
async def generate_next_number(request: Request):
    data = await request.json()
    room_id = data['room_id']

    await increment_bingo_pull_count(room_id)

    pull_count = await get_bingo_pull_count(room_id)
    if pull_count > 2:
        number = random.randint(0, 100)

        while await check_bingo_number(room_id, number):
            number = random.randint(0, 100)

        await insert_bingo_number(room_id, number)
        await insert_bingo_number_history(room_id, number)
        await reset_pull_count(room_id)

@app.post("/pull_bingo_number")
async def pull_bingo_number(request: Request):
    try:
        data = await request.json()
        room_id = data['room_id']
        number = await get_bingo_number(room_id)
        print("Room:", room_id, "Number:", number)

        return {"number": number}

    except KeyError:
        raise HTTPException(status_code=400, detail="Room ID is missing.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create_Bingo_Session Route
@app.get("/bingo_mp")
async def bingo_mp(request: Request, background_tasks: BackgroundTasks):
    request.session["bingo_numbers"] = []
    ## If room is created after another user has been created in the same browser player1 = player2 -- ERROR

   # Generate a random room ID from ShortUUID
    room_id_gen = shortuuid.ShortUUID("23456789ABCDEF")
    room_id = room_id_gen.random(4)

    # Get the username and Save the room_id to the HTTP cookie
    user = request.session["username"]
    request.session["room_id"] = room_id

    # Create the room with the room_id and the Host
    background_tasks.add_task(insert_bingo_room_sync, room_id, user)

    if await get_bingo_player_one(room_id) != None:
        redirect_url = f"/bingo_mp/{room_id}_h"
    else:
        # Append the token to the URL and redirect to the create_session page
        redirect_url = f"/bingo_mp/{room_id}"

    return RedirectResponse(url=redirect_url)

# Bingo game route
@app.get("/bingo_menu")
async def bingo_menu(request: Request):
    username = request.session.get("username", "guest")
    return templates.TemplateResponse("bingo_menu.html", {"request": request, "USERNAME": username})

# Create_Bingo_Session with Token Route redirect
@app.get("/bingo_mp/{room_id}")
async def create_bingo_session_with_token(request: Request, room_id: str):
    # Render the create_session page with the token
    return templates.TemplateResponse("bingo_mp.html", {"request": request, "room_id": room_id})

# Join_Bingo_Session Route
@app.post("/join_bingo_mp")
async def join_bingo_session(request: Request, background_tasks: BackgroundTasks, room_id: str = Form(...)):

    # Get the username from the HTTP cookie and join the room
    user = request.session.get("username")
    room = room_id
    background_tasks.add_task(join_bingo_room_sync, room, user)

    # Construct the redirect URL
    redirect_url = f"/bingo_mp/{room_id}"

    # Return a redirect response to the URL
    return RedirectResponse(url=redirect_url, status_code=303)

# Websocket Endpoint
@app.websocket("/ws/{page}/{room_id}")

#Weboscket connection parameters:
#page: the page initiating the websocket connection
#room_id: the room ID for the room the user is joining/hosting
#username: the username of the user connecting to the websocket enconded within websocket URL as a query parameter

async def websocket_endpoint(websocket: WebSocket, page: str, room_id: str, username: str = Query(None)):
    await websocket.accept()
    # Debug print the username and Initialize the position
    print("Recieved WS Username:", username)
    position = 0
    bingo_status = False
    print(page)
    try:
        # Loop to receive data from the client and Update the page with the room details
        while True:
            if page == "create_room":
                try:
                    # Await the data from the client, then insert the move into the database. Timeout 0.1 seconds
                    data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                    move = data["move"]
                    if data:
                        print(f"Received data: {data}")
                        await insert_room_move(room_id, move, position)


                except asyncio.TimeoutError:
                    # Fetch room details from the database and send it to the client
                    room = room_id
                    player_1 = await get_player_one(room_id)
                    player_2 = await get_player_two(room_id)

                    # Calculate the position of the player
                    if player_1 == username:
                        position = 1
                    else:
                        position = 2

                    # Construct the JSON data to send to the client and send it
                    data_to_send = json.dumps({"room": room, "player_1": player_1, "player_2": player_2})
                    await websocket.send_text(data_to_send)

                    # Check if both players have moved and determine the winner
                    await rock_paper_scissors(room_id)

                    # Pause for 2 seconds before the next iteration
                    await asyncio.sleep(2)
            elif page == "bingo_mp":
                try:
                     # Await the data from the client, then insert the move into the database. Timeout 0.1 seconds
                    data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)

                    if "start_game" in data:
                        bingo_status = True
                        await set_room_active(room_id)
                    else:
                        bingo_status = False

                    if await is_room_active(room_id):
                        bingo_status = True

                    if data:
                        print(f"Received data: {data}")


                except asyncio.TimeoutError:
                    # Fetch room details from the database and send it to the client
                    room = room_id
                    player_1 = await get_bingo_player_one(room_id)
                    player_2 = await get_bingo_player_two(room_id)
                    bingo_status = await is_room_active(room_id)
                    number = await get_bingo_number(room_id)


                    # Construct the JSON data to send to the client and send it
                    data_to_send = json.dumps({"room": room, "player_1": player_1, "player_2": player_2, "game_status": bingo_status, "number": number})
                    await websocket.send_text(data_to_send)


                    # Pause for 2 seconds before the next iteration
                    await asyncio.sleep(2)

    except WebSocketDisconnect:
        # Close the websocket connection if the client disconnects
        print(f"WebSocket disconnected for room {room_id} on page {page}")

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        await websocket.close(code=1011, reason="Unexpected error")

