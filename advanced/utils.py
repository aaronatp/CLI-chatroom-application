import sqlite3


def query_exists_short(response):
    """Essentially checking whether a given room name exists"""
    conn = sqlite3.connect("chatroom_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT room_name FROM rooms WHERE room_name=?", (response,))
    if cursor.fetchall():
        conn.close()
        return True

    conn.close()
    return False


def query_exists_long(response):
    """Checking whether a given username exists"""
    if response is None:
        return False

    conn = sqlite3.connect("chatroom_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administrative WHERE users=?", (response,))
    if cursor.fetchall():
        conn.close()
        return True
    else:
        conn.close()
        return False


def get_password_from_username(user):
    """
    Given a username, we query the database and retrieve the user's password.
    We use this to ensure that the user-supplied password matches the password we previously stored.
    """
    conn = sqlite3.connect("chatroom_app.db")
    cursor = conn.cursor()
    print(f"user == {user}")
    print(f"type of user == {type(user)}")

    cursor.execute("SELECT passwords FROM administrative WHERE users=?", (user,))
    counter = 0
    for password in cursor.fetchall():
        counter += 1
        assert(counter != 2)  # this and the assert statement below ensure there is only one password in the cursor.fetchall() list
        return password[0]
    
    assert(counter != 0)


def create_user_and_password(username, password):
    """
    adds username and password to users and passwords columns in administrative table
    """
    conn = sqlite3.connect("chatroom_app.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO administrative (users, passwords) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()


def get_room_content_from_db(room):
    """Given a room name, we query the database and retrieve the room's contents"""
    conn = sqlite3.connect("chatroom_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT room_content FROM rooms WHERE room_name=?", (room,))  # ensure you don't fuck oup the database mwehn you change room_content
    counter = 0
    for room_content in cursor.fetchall():
        conn.close()
        counter += 1
        assert(counter != 2)  # if this fails, does that fetchall() returned multiple room content values?
        conn.close()
        return room_content[0]
    
    conn.close()  # we should never reach here
    assert(counter != 0)  # make sure you don't pass the room_content variable again lol


def add_room_in_rooms_table(room_name):
    """
    adds room to room_names column
    """
    conn = sqlite3.connect('chatroom_app.db')
    conn.execute("INSERT INTO rooms (room_name, room_content, room_update) VALUES (?, ?, ?)", (room_name, '', '0',))
    conn.commit()
    conn.close()
    return
