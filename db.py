import aiomysql
# Database Functions

# Function to establish a connection to the database
async def get_db_connection():
    return await aiomysql.connect(host='mascaro101.mysql.pythonanywhere-services.com',
                                  user='mascaro101',
                                  password='laquegana123',
                                  db='mascaro101$CasinoDB',
                                  charset='utf8mb4',
                                  cursorclass=aiomysql.DictCursor)

# Rooms Table Functions
# Create Rooms Table
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

# Create Bingo Rooms Table
async def create_bingo_rooms_table():
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS bingo_rooms (
                    room_id VARCHAR(100) PRIMARY KEY,
                    room_active TINYINT,
                    pull_count INT,
                    bingo_number VARCHAR(100),
                    player_1 VARCHAR(100) NOT NULL,
                    player_2 VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await connection.commit()
    finally:
        connection.close()

async def check_bingo_number(room_id, number):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            # Check if the number exists under the given room_id
            await cursor.execute(
                "SELECT 1 FROM bingo_history WHERE room_id = %s AND bingo_number = %s LIMIT 1",
                (room_id, number)
            )
            result = await cursor.fetchone()
            return result is not None
    finally:
        await connection.ensure_closed()


# Create Bingo History Table
async def create_bingo_history():
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS bingo_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    room_id VARCHAR(100),
                    bingo_number VARCHAR(100)
                )
            ''')
            await connection.commit()
    finally:
        await connection.ensure_closed()  # Close the connection asynchronously

# Function to insert a new bingo room into the rooms table
async def insert_bingo_number_history(room_id, bingo_number):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            # First INSERT statement
            await cursor.execute(
                "INSERT INTO bingo_history (room_id, bingo_number) VALUES (%s, %s)",
                (room_id, bingo_number)
            )
            # Commit the transaction
            await connection.commit()
    except aiomysql.Error as e:
        print(f"An error occurred: {e}")
        await connection.rollback()
    finally:
        connection.close()

# Function to join a bingo room from room_id
async def join_bingo_room_sync(room_id: str, player_2: str):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE bingo_rooms SET player_2 = %s WHERE room_id = %s",
                (player_2, room_id)
            )
            await connection.commit()
    finally:
        connection.close()

# Function to insert a new bingo room into the rooms table
async def insert_bingo_room_sync(room_id, player_1):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            # First INSERT statement
            await cursor.execute(
                "INSERT INTO bingo_rooms (room_id, room_active, bingo_number, pull_count, player_1, player_2) VALUES (%s, %s, %s, %s, %s, %s)",
                (room_id, 0, "!", 0, player_1, "Waiting For Player 2")
            )
            # Commit the transaction
            await connection.commit()
    except aiomysql.Error as e:
        print(f"An error occurred: {e}")
        await connection.rollback()
    finally:
        connection.close()

async def increment_bingo_pull_count(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE bingo_rooms SET pull_count = pull_count + 1 WHERE room_id = %s", (room_id,))
            await connection.commit()
    finally:
        connection.close()

async def get_bingo_pull_count(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT pull_count FROM bingo_rooms WHERE room_id = %s", (room_id,))
            result = await cursor.fetchone()
            return result['pull_count'] if result else 0
    finally:
        connection.close()

async def reset_pull_count(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE bingo_rooms SET pull_count = 0 WHERE room_id = %s", (room_id,))
            await connection.commit()
    finally:
        await connection.close()

# Function to get the player_2 from the rooms table
async def get_bingo_player_two(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT player_2 FROM bingo_rooms WHERE room_id = %s", (room_id,))
            result = await cursor.fetchone()
            if result:
                return result['player_2']
            else:
                return "No room found with the given ID"
    finally:
        connection.close()

# Function to get the bingo player_1 from the rooms table
async def get_bingo_player_one(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT player_1 FROM bingo_rooms WHERE room_id = %s", (room_id,))
            result = await cursor.fetchone()
            if result:
                return result['player_1']
            else:
                return "No room found with the given ID"
    finally:
        connection.close()

# Function to insert a new move into the room_moves table
async def insert_bingo_number(room_id, number):
    connection = await get_db_connection()
    print("Started Insert to", room_id)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE bingo_rooms SET bingo_number = %s WHERE room_id = %s",
                (number, room_id)
            )

            await connection.commit()
    finally:
        connection.close()


# Function to insert a new room into the rooms table
async def insert_room_sync(room_id, player_1):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            # First INSERT statement
            await cursor.execute(
                "INSERT INTO rooms (room_id, player_1, player_2) VALUES (%s, %s, %s)",
                (room_id, player_1, "Waiting For Player 2")
            )
            # Second INSERT statement
            await cursor.execute(
                "INSERT INTO room_moves (room_id, player_1_moves, player_2_moves) VALUES (%s, %s, %s)",
                (room_id, "No Moves", "No Moves")
            )
            # Commit the transaction
            await connection.commit()
    except aiomysql.Error as e:
        print(f"An error occurred: {e}")
        await connection.rollback()
    finally:
        connection.close()

async def set_room_active(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                    "UPDATE bingo_rooms SET room_active = %s WHERE room_id = %s",
                    (1, room_id)
                )
            await connection.commit()
    finally:
        connection.close()

async def get_bingo_number(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT bingo_number FROM bingo_rooms WHERE room_id = %s", (room_id,))
            result = await cursor.fetchone()
            return result["bingo_number"]
    finally:
        connection.close()

async def is_room_active(room_id):
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT room_active FROM bingo_rooms WHERE room_id = %s", (room_id,))
            result = await cursor.fetchone()
            if result["room_active"] == 1:
                return True
            return False
    finally:
        connection.close()

# Function to get the player_1 from the rooms table
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

# Function to get the player_2 from the rooms table
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

# Room Moves Table Functions
# Create Room Moves Table
async def create_room_moves_table():
    connection = await get_db_connection()
    try:
        async with connection.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS room_moves (
                    move_id INT AUTO_INCREMENT,
                    room_id VARCHAR(100),
                    player_1_moves VARCHAR(100),
                    player_2_moves VARCHAR(100),
                    PRIMARY KEY(move_id, room_id),
                    FOREIGN KEY(room_id) REFERENCES rooms(room_id)
                )
            ''')
            await connection.commit()
    finally:
        connection.close()

# Function to insert a new move into the room_moves table
async def insert_room_move(room_id, move, position):
    connection = await get_db_connection()
    print("Started Insert to", room_id, move)
    print("Position:", position)
    try:
        if position == 1:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "UPDATE room_moves SET player_1_moves = %s WHERE room_id = %s",
                    (move, room_id)
                )
                await connection.commit()

        elif position == 2:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "UPDATE room_moves SET player_2_moves = %s WHERE room_id = %s",
                    (move, room_id)
                )
                await connection.commit()
    finally:
        connection.close()

# Function to join a room from room_id
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

# Function to check if both players have moved
async def have_both_moved(room_id):
    connection = await get_db_connection()
    player_status = []
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT player_1_moves FROM room_moves WHERE room_id = %s", (room_id,))
            result_player_1 = await cursor.fetchone()

            if result_player_1 != "No Moves":
                player_status.append(True)


            await cursor.execute("SELECT player_2_moves FROM room_moves WHERE room_id = %s", (room_id,))
            result_player_2 = await cursor.fetchone()

            if result_player_2 != "No Moves":
                player_status.append(True)

        if len(player_status) == 2:
            return True, result_player_1, result_player_2
        else:
            player_status = []
            return False, None, None
    finally:
        connection.close()