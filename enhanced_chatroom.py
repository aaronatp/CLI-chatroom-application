
import asyncio
import sqlite3
import pdb
from multiprocessing import Process, Queue

import aioconsole


class ChatApp:
    """
    We initialize a class instance in 'if __name__ == "__main__":', look there for more information.
    """
    def __init__(self, current_user, current_room):
        # self.users = users
        # self.rooms = rooms
        self.current_user = current_user
        self.current_room = current_room


    def ensure_db_initialized(self):
        conn = sqlite3.connect("chatroom_app.db")

        # create a table (if it doesn't already exist)
        with conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS administrative (
                            users,
                            passwords
                        );""")
            
            conn.execute("""CREATE TABLE IF NOT EXISTS rooms (
                         room_name,
                         room_content,
                         room_update
            );""")


    def ensure_logged_in(self):
        '''
        Before users can access a chatroom, we make sure they are logged in.

        If they're not, we ask them to log in or create an account.
        '''        
        if query_exists_long(self.current_user):
            return True

        while True:
            print("Do you have an account or do you want to create one?\n\na) Log in to my account\nb) Create account\n\n")
            answer = input("> ").lower()  # Convert input to lowercase for case-insensitive comparison

            if answer == 'a':
                if self.log_in():
                    return True  # exit the loop if login is successful
            elif answer == 'b':
                if self.create_account_and_log_in():
                    return True  # exit the loop if account creation is successful
            else:
                print("\nInvalid option. Please enter 'a' to log in or 'b' to create an account.")


    def log_in(self):
        """
        Helps users log in.
        """
        while True:
            print("Press 'q' to return to the main menu")
            print("What is your username?")
            
            username = input("> ")
            if username == 'q':
                return False
            
            if not query_exists_long(username):   # if this runs, username does not exist
                print("Invalid username!\n")
                continue

            self.current_user = username
            print(f"Thank you, {username}!")

            # if we reach here, user has given valid username
            while True:
                print("What is your password?")
                print("Press 'q' to return to the main menu")
                password = input("> ")
                if password == 'q':
                    return False
                
                elif password != get_password_from_username(username):
                    print("Incorrect password!\n")
                    continue

                return True
        

    def create_account_and_log_in(self):
        """
        Creates account and logs user in.
        """
        print("Press 'q' to return to the main menu")
        print("Please create a username")
        username = input("> ")
        if username == 'q':
            return False

        print("Please create a password")
        password = input("> ")
        create_user_and_password(username, password)
        self.current_user = username

        return True


    async def get_chat_room(self):
        """
        Gets chatroom for user. Users can either access an existing one, or create a new one.

        This method leaves creation/joining chatrooms to callees.
        """
        print("Congratulations on logging in!")

        while True:
            await aioconsole.aprint("Press 'a' to join a shared chat room or 'b' to create your own")
            response = await aioconsole.ainput("> ")
            if response == 'a':
                return await self.join_room()  # after this function returns, by default we prepare to end the program
            elif response == 'b':
                response = await self.try_create_room()
                continue
            else:
                await aioconsole.aprint(f"Invalid choice: \"{response}\"")
                continue


    async def try_create_room(self):
        """
        This function only creates and initializes the room.
        
        It leaves it to the 'join_room' method to actually join the room.
        """
        while True:
            await aioconsole.aprint("What is the name of the chat room you want to create?")
            await aioconsole.aprint("Press 'q' to return to the main menu")
            response = await aioconsole.ainput("> ")
            if response == 'q':
                return False
            
            if query_exists_short(response):
                await aioconsole.aprint(f"{response} already exists. Do you want to return to the main menu to join it?")
                answer = await aioconsole.ainput("> ")
                if answer == 'yes':
                    return
                elif answer == 'no':
                    await aioconsole.aprint("ok!")
                    continue
                else:
                    await aioconsole.aprint("Please write 'yes' or 'no'!\n")
                    continue

            # create new row in rooms database table
            # if 
                
            add_room_in_rooms_table(response)
            await aioconsole.aprint(f"Congratulations! You've created room {response}")
            return

            # else:
            #     # couldn't create room - print some debugging details (this has happened, not quite sure why)
            #     await aioconsole.aprint(f"Failed to create {response} room")  # check if there are duplicates etc
            #         # have different return here
        

    async def join_room(self):
        """
        Joins a chatroom and when there is data from one of them,
        this function updates the ChatApp.rooms attribute (essentially
        it updates/stores the content associated with the chatroom).
        """
        while True:
            await aioconsole.aprint("What is the name of the room you would like to join?")
            await aioconsole.aprint("Press 'q' to return to the main menu")
            response = await aioconsole.ainput("> ")
            if response == 'q':
                return False
            
            elif not query_exists_short(response):  # if this runs, the room does not exist
                await aioconsole.aprint("Room doesn't exist!\n")
                await aioconsole.aprint("If you would like to create the room, please return to the main menu")
                continue

            else:
                chatroom = SharedChat(self.current_user, response)
                return await chatroom.join_chat(response)


    async def run(self):
        counter = 0
        while True:
            counter +=1
            # print(f"we enter counter for the {counter} timeee\n\n\n")
            self.ensure_db_initialized()
            self.ensure_logged_in()
            await self.get_chat_room()  # probably one of the awaitables in the subchat join_chat function doesnt terminate

            subcounter = 0
            while True:
                subcounter += 1
                print(f"are we having an inssue with subcounter? == {subcounter}")
                await aioconsole.aprint("Do you want to log off? (yes/no)")
                answer = await aioconsole.ainput("> ")
                print("do we go past here?")
                if answer == 'yes':
                    self.current_user = None
                    self.current_room = None
                    await aioconsole.aprint("Goodbye!")
                    return
                
                elif answer == 'no':
                    # await aioconsole.aprint("we're still running")
                    # await aioconsole.aprint(f"current user == {self.current_user}")
                    break

                else:
                    await aioconsole.aprint("\nPlease answer 'yes' or 'no'!")


def query_exists_short(response):
    conn = sqlite3.connect("chatroom_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT room_name FROM rooms WHERE room_name=?", (response,))
    if cursor.fetchall():
        conn.close()
        return True

    conn.close()
    return False


def query_exists_long(response):
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


def get_room_content_from_db(room):  # calling this seems to duplicate
    # print("are we calling our precious every time?")
    conn = sqlite3.connect("chatroom_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT room_content FROM rooms WHERE room_name=?", (room,))  # ensure you don't fuck oup the database mwehn you change room_content
    counter = 0
    # print(f"we're in room_content print cursor.fetchall(): {cursor.fetchall()[0]}")
    # cursor.execute("SELECT room_content FROM rooms WHERE room_name=?", (room,))
    for room_content in cursor.fetchall():
        conn.close()
        counter += 1
        assert(counter != 2)  # if this fails, does that fetchall() returned multiple room content values?
        # print(f"type of get_room_content == {type(room_content[0])}")
        # print(f"get_room_content itself == {room_content[0]}")
        conn.close()
        return room_content[0]
    
    # print(f"inspect cursor: {cursor.fetchall()[0]}")
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


class SharedChat(ChatApp):
    """
    Look at the comments at the start of the program for general
    details about this class' function/position in the program
    
    This class manages chat "instances." Each user/room is an instance.
    Different users in the same room access the chat through different
    SharedChat instances.
    """
    def __init__(self, current_user, room):
        super().__init__(current_user, current_room)
        self.current_room = room  # note, we override the parent class' self.current_room method
        self.room_content = ''


    async def update_room_content_class_db(self, message, room):  # ensure 'message' here is already beautified 
        conn = sqlite3.connect("chatroom_app.db")
        cursor = conn.cursor()

        pre_update_content = self.room_content
        if self.room_content == '':  # if we're just joining the chat, we check if there's previous chat history - if not, we initialize with ''
            pre_update_content = get_room_content_from_db(room)

        self.room_content = pre_update_content + message  # basically gets the current room content and appends user's message

        cursor.execute("UPDATE rooms SET room_content=? WHERE room_name=?", (self.room_content, room,))
        conn.commit()
        conn.close()

        # print("ran conn close - do we finish the update class/db func?")
        return
    

    # def check_if_new_messages(self):
    #     # if check_need_to_update():
    #     conn = sqlite3.connect("chatroom_app.db")
    #     cursor = conn.cursor()
    #     print("are we doing it")
    #     cursor.execute("SELECT room_update FROM rooms WHERE room_name=?", (self.current_room,))
    #     print("did we select our get update value")
    #     # print(f"cursor.fetchone()[0] == {cursor.fetchone()[0]}")
    #     if cursor.fetchone()[0] == '1':
    #         print("did we find something?")
    #         # breakpoint()
    #         db_content = get_room_content_from_db(self.current_room)
    #         print(f"db_content == {db_content}")
    #         print("do we complete db content retrieve")
    #         print(f"self.current_room == {self.current_room}")
    #         print("do we finish getting current room")
    #         cursor.execute("UPDATE rooms SET room_content=? WHERE room_name=?", (db_content, self.current_room,))
    #         cursor.execute("UPDATE rooms SET room_update=? WHERE room_name=?", ('0', self.current_room,))
    #         print("did we update the room update value?")
    #         # print(get_room_content_from_db(self.current_room))
    #         conn.commit()
    #         conn.close()
    #         return True
        
    #     conn.commit()
    #     conn.close()
    #     return False


    async def get_and_handle_user_input(self):
        while True:
            conn = sqlite3.connect("chatroom_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT room_update FROM rooms WHERE room_name=?", (self.current_room,))
            if cursor.fetchall()[0] == '1':
                self.room_content = get_room_content_from_db(self.current_room)
                print(get_room_content_from_db(self.current_room), flush=True)
                cursor.execute("UPDATE rooms set room_update=? WHERE room_name=?", ('0', self.current_room,))
                conn.commit()
            conn.close()

            raw_message = await aioconsole.ainput("> ")  # third-party asynchronous implementation of python's built-in "input()" function
            if raw_message == 'q':
                return False

            bubble = SpeechBubble(self.current_user, raw_message)
            # beautified_message = await bubble.beautify()
            # updates room content in class attribute and prints message (happens under the hood)
            # self.room_content += beautified_message
            # update room content in class attribute and database

            new_content = get_room_content_from_db(self.current_room).replace(self.room_content, "")
            print(f"new content == {new_content}")

            await self.update_room_content_class_db(await bubble.beautify(), self.current_room)  # add user input to database - should the be a class method or unattached (does it rely on aioconsole?)
    

    # async def check_update_room_content(self, queue, room):  # async_generator
    #     """
    #     This runs in a subprocess.
        
    #     Essentially queries database for updates, then provides user with updates.
    #     """
    
    #     while True:  # implement some error handling
    #         asyncio.sleep(1)
    #         conn = sqlite3.connect("chatroom_app.db")
    #         cursor = conn.cursor()
    #         new_content = get_room_content_from_db(room).replace(self.room_content, "")  # essentially take the difference of the most current string and the previous to find new messages
    #         if new_content != '':
    #             queue.put('the number 5 haha')
    #             queue.put(new_content)
    #             queue.put(' the number 2 hoho')
    #             cursor.execute("UPDATE rooms SET room_content=? WHERE room_name=?", (new_content, room,))
    #             cursor.execute("UPDATE rooms SET room_update=? WHERE room_name=?", ('1', room,))
    #             conn.commit()

    #         conn.close()
            
    # async def thin_wrapper(self, queue, room):
    #     async for i in async_generator(queue, room):  # do you have to use 'await' here?
    #         yield queue.get()


    async def run_chat_routine(self):  # this func may leave an awaitable open which fucks up the run function
        # only create a new process for the check update content
        # queue = Queue()
        # run_check_update_content = Process(target=self.check_update_room_content, args=(queue, self.current_room,), daemon=True)
        # run_check_update_content.start()  # checks/updates content database in a while True loop under the hood
        
        # asyncio.create_task(self.thin_wrapper)

        # while True:
        #     queue.get()

        # async asyncio.gather(
        #     run_check_update_content,
        #     self.get_and_handle_user_input,
        #     )

        # breakpoint()
        keep_going = await self.get_and_handle_user_input()  # also a while True loop under the hood

        # breakpoint()
        if not keep_going:
            # run_check_update_content.terminate()
            # run_check_update_content.close()
            return


    async def join_chat(self, room: str):
        """
        User types messages here. This function also periodically check whether other users have
        added to the chat, and if so, this method fetches the "updated" chat.
        
        This method delegates to the SpeechBubble class to beautify the messages.

        Caller performs error checking for the room name.
        """
        chat_history = get_room_content_from_db(room)
        if chat_history == '':
            await aioconsole.aprint(f"Congratulations on joining {room}!")
            await aioconsole.aprint("Send a message!")

        else:
            await aioconsole.aprint(chat_history)  # we print the chat history if it's not empty

        await aioconsole.aprint("Press 'q' to leave")

        try:
            return await self.run_chat_routine()
        except BlockingIOError:
            raise  # run with '-u' flag (like so, "python -u ./chatroom_app.py") - (https://stackoverflow.com/questions/230751/how-can-i-flush-the-output-of-the-print-function/230780#230780)


class SpeechBubble:
    def __init__(self, username, text, line_length=50, inner_line_length=45):
        self.username = username
        self.text = text
        self.line_length = line_length
        self.inner_line_length = inner_line_length

    
    def wrap_multi_line(self, username, text):
        wrapped_text = f"{username}: "
        current_line = ""
        for word in text.split():
            if len(current_line) + len(word) > self.inner_line_length:
                if len(current_line) > 0:
                    wrapped_text += current_line + " |\n"
                current_line = f"|{word}"
            else:
                current_line += f" {word}"
    
            if len(current_line) + len(word) > self.line_length:
                wrapped_text += current_line + "\n"
                current_line = word   

        if len(current_line) > 0:
            wrapped_text += current_line
                
        return wrapped_text.strip()


    async def beautify(self):
        top = "-" * self.line_length
        bottom = "-" * self.line_length
        body = f"| {self.wrap_multi_line(self.username, self.text)} |"
        await aioconsole.aprint(top)
        await aioconsole.aprint(body)
        await aioconsole.aprint(bottom)
        return top + "\n" + body + "\n" + bottom


if __name__ == "__main__":
    __spec__ = None  # to avoid a stupid error raised when using pdb (https://stackoverflow.com/questions/45720153/python-multiprocessing-error-attributeerror-module-main-has-no-attribute/60922965?noredirect=1#comment83471090_45720872)
    # in reality, these variables would probably be stored in other files or a database etc.
    # I have initialized them here for the sake of keeping this program self-contained
    # users = {'user1': 'password', 'user2': 'other password'}  # dictionary for storing users and passwords
    # rooms = {}  # associates rooms with room-content (e.g., messages, etc.)
    current_user = None
    current_room = None

    app = ChatApp(current_user, current_room)
    asyncio.run(app.run())

