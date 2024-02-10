import asyncio
import sqlite3
from multiprocessing import Process, Queue
from concurrent.futures import CancelledError

import utils
from speech_bubble import SpeechBubble

from aioconsole import ainput, aprint  # asynchronous implementations of python's built-in "input()" and "print()" functions


class ChatApp:
    """
    We initialize a class instance in 'if __name__ == "__main__":', look there for more information.
    """
    def __init__(self, current_user, current_room):
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
        if utils.query_exists_long(self.current_user):
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
            
            if not utils.query_exists_long(username):   # if this runs, username does not exist
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
                
                elif password != utils.get_password_from_username(username):
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
        utils.create_user_and_password(username, password)
        self.current_user = username
        return True


    async def get_chat_room(self):
        """
        Gets chatroom for user. Users can either access an existing one, or create a new one.

        This method leaves creation/joining chatrooms to callees.
        """
        print("Congratulations on logging in!")

        while True:
            await aprint("Press 'a' to join a shared chat room or 'b' to create your own")
            response = await ainput("> ")
            if response == 'a':
                return await self.join_room()
            elif response == 'b':
                response = await self.try_create_room()
                continue
            else:
                await aprint(f"Invalid choice: \"{response}\"")
                continue


    async def try_create_room(self):
        """
        This function only creates and initializes the room.
        
        It leaves it to the 'join_room' method to actually join the room.
        """
        while True:
            await aprint("What is the name of the chat room you want to create?")
            await aprint("Press 'q' to return to the main menu")
            response = await ainput("> ")
            if response == 'q':
                return False

            if utils.query_exists_short(response):
                await aprint(f"{response} already exists. Do you want to return to the main menu to join it?")
                answer = await ainput("> ")
                if answer == 'yes':
                    return
                elif answer == 'no':
                    await aprint("ok!")
                    continue
                else:
                    await aprint("Please write 'yes' or 'no'!\n")
                    continue

            utils.add_room_in_rooms_table(response)
            await aprint(f"Congratulations! You've created room {response}")
            return
        

    async def join_room(self):
        """
        Joins a chatroom and when there is data from one of them,
        this function updates the ChatApp.rooms attribute (essentially
        it updates/stores the content associated with the chatroom).
        """
        while True:
            await aprint("What is the name of the room you would like to join?")
            await aprint("Press 'q' to return to the main menu")
            response = await ainput("> ")
            if response == 'q':
                return False

            elif not utils.query_exists_short(response):  # if this runs, the room does not exist
                await aprint("Room doesn't exist!\n")
                await aprint("If you would like to create the room, please return to the main menu")
                continue

            else:
                chatroom = SharedChat(self.current_user, response, '')  # we pass '' here because it simplifies subclassing later
                return await chatroom.join_chat(response)


    async def run(self):
        while True:
            self.ensure_db_initialized()
            self.ensure_logged_in()
            await self.get_chat_room()

            while True:
                await aprint("Do you want to log off? (yes/no)")
                answer = await ainput("> ")
                if answer == 'yes':
                    self.current_user = None
                    self.current_room = None
                    await aprint("Goodbye!")
                    return
                
                elif answer == 'no':
                    break

                else:
                    await aprint("\nPlease answer 'yes' or 'no'!")


class SharedChat(ChatApp):
    """
    Look at the comments at the start of the program for general
    details about this class' function/position in the program
    
    This class manages chat "instances." Each user/room is an instance.
    Different users in the same room access the chat through different
    SharedChat instances.
    """
    def __init__(self, current_user, room, room_content):
        super().__init__(current_user, current_room)
        self.current_room = room  # note, we override the parent class' self.current_room method
        self.room_content = room_content


    async def update_room_content_class_db(self, message, room):  # ensure 'message' here is already beautified 
        conn = sqlite3.connect("chatroom_app.db")
        cursor = conn.cursor()

        pre_update_content = self.room_content
        if self.room_content == '':  # if we're just joining the chat, we check if there's previous chat history - if not, we initialize with ''
            pre_update_content = utils.get_room_content_from_db(room)

        self.room_content = pre_update_content + message  # basically gets the current room content and appends user's message
        cursor.execute("UPDATE rooms SET room_content=? WHERE room_name=?", (self.room_content, room,))
        conn.commit()
        conn.close()
        return


    async def get_and_handle_user_input(self):
        while True:
            conn = sqlite3.connect("chatroom_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT room_update FROM rooms WHERE room_name=?", (self.current_room,))
            if cursor.fetchall()[0] == '1':
                self.room_content = utils.get_room_content_from_db(self.current_room)
                # aprint(utils.get_room_content_from_db(self.current_room), flush=True)
                cursor.execute("UPDATE rooms set room_update=? WHERE room_name=?", ('0', self.current_room,))
                conn.commit()
            conn.close()

            raw_message = await ainput("> ")
            if raw_message == 'q':
                conn = sqlite3.connect("chatroom_app.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE rooms set room_update=? WHERE room_name=?", ('-1', self.current_room,))
                conn.commit()
                conn.close()
                raise CancelledError

            bubble = SpeechBubble(self.current_user, raw_message)
            await self.update_room_content_class_db(await bubble.beautify(), self.current_room)  # add user input to database - should the be a class method or unattached (does it rely on aioconsole?)
    

    async def check_update_room_content(self, queue, room):  # async_generator
        """
        This runs in a subprocess. Every user runs this checker function. It looks to see whether
        other users have sent messages. It does this by querying the room_content table of the rooms database
        and checks whether the room_content in the shared database is different from the user's local version
        (stored in the SharedClass.room_content class attribute).

        If there is new content in a chatroom, this function sets the "room_update" column to '1'.
        The main process (what function in it?) queries the "room_update" column, and when it is equal to '1', the main process
        fetches the new content. This is how users chat instances are notified when other users send messages.

        Finally, this function sends new messages to a wrapper function in the main process which prints
        the messages.
        
        Some error handling performed by the caller function.
        """
    
        while True:
            await asyncio.sleep(1)
            conn = sqlite3.connect("chatroom_app.db")
            cursor = conn.cursor()
            new_content = utils.get_room_content_from_db(room).replace(self.room_content, "")  # essentially take the difference of the most current string and the previous to find new messages
            if new_content != '':
                # add new_content to database
                # cursor.execute("UPDATE rooms SET room_content=? WHERE room_name=?", (new_content, room,))
                cursor.execute("UPDATE rooms SET room_update=? WHERE room_name=?", ('1', room,))
                conn.commit()
                conn.close()

                # send new_content to parent process which will handle/print it
                yield queue.put_nowait(new_content)
                continue

            conn.close()

    # make sure 'q' quits the chat program
    # add in like 25 spaces between each printing
    # improve functions documentation
    # refactor into a few files
    async def thin_wrapper(self, room, room_content, queue):
        """
        
        multiprocessing.Queue raises "_queue.Empty" if we try to 'get' from a subprocess when nothing is put

        "_queue.Empty" is an empty object with no attributes. It is difficult to specifically filter those
        errors so we ignore all TypeErrors errors with no attributes.
        """
        async for _ in CheckUpdateRoomContent(room, room_content, queue):
            if _ == -1:  # see 'self.run_chat_routine' - this works around a bug in asyncio.gather where it will keep yielding forever
                try:
                    # empty queue if we have to (can't join process if queue is not empty)
                    while True:
                        queue.get_nowait()

                except:
                    pass

                return

            try:
                await aprint('\n' * 25 + queue.get_nowait())
            except Exception as e:
                try:
                    if "_queue.Empty" in e:
                        continue
                except TypeError:
                    if len(e.__dict__) == 0:  # looks like 'e' is 
                        pass
                    else:
                        raise f"Uh oh! What happened here?\ne.__dict__ == {e.__dict__}"


    async def run_chat_routine(self):
        # only create a new process for the check update content
        queue = Queue()
        run_check_update_content = Process(target=self.check_update_room_content, args=(queue, self.current_room,))
        run_check_update_content.start()  # checks/updates content database in a while True loop under the hood
        assert(run_check_update_content.is_alive() == True)
        # unfortunately, there doesn't seem to be any clean way to simply exist asyncio.gather
        # when the user wants to leave, 'get_and_handle_user_input' raises a LeaveRoomException under the hood
        
        try:
            # this workaround is due to a bug where asyncio.gather won't quit (https://stackoverflow.com/questions/69997653/python-asyncio-gather-does-not-exit-after-task-complete)
            await asyncio.gather(
                self.thin_wrapper(self.current_room, self.room_content, queue),
                self.get_and_handle_user_input(),
            )

        except CancelledError:
            # kill the child process
            run_check_update_content.join()
            while run_check_update_content.is_alive() == True:  # if True, check again every second until False
                await asyncio.sleep(1)
                await aprint("checking again...")

        return


    async def join_chat(self, room: str):
        """
        User types messages here. This function also periodically check whether other users have
        added to the chat, and if so, this method fetches the "updated" chat.
        
        This method delegates to the SpeechBubble class to beautify the messages.

        Caller performs error checking for the room name.
        """
        chat_history = utils.get_room_content_from_db(room)
        if chat_history == '':
            await aprint(f"Congratulations on joining {room}!")
            await aprint("Send a message!")

        else:
            await aprint(chat_history)  # we print the chat history if it's not empty

        await aprint("Press 'q' to leave")

        try:
            return await self.run_chat_routine()
        except BlockingIOError:
            raise  "Run this program with the Python '-u' flag (like so, 'python -u ./chatroom_app.py')" # - (https://stackoverflow.com/questions/230751/how-can-i-flush-the-output-of-the-print-function/230780#230780)
        

class CheckUpdateRoomContent(SharedChat):
    def __init__(self, current_room, room_content, queue):
        super().__init__(current_user, current_room, room_content)
        self.queue = queue


    async def __anext__(self):
        while True:
            # hacky work-around for bug in asyncio.gather (also see 'self.run_chat_rountine' and 'self.thin_wrapper')
            conn = sqlite3.connect("chatroom_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT room_update FROM rooms WHERE room_name=?", (self.current_room,))
            if str('-1') in cursor.fetchall() or int('-1') in cursor.fetchall():
                conn.close()
                return self.queue.put_nowait(-1)
            conn.close()

            await asyncio.sleep(1)
            conn = sqlite3.connect("chatroom_app.db")
            cursor = conn.cursor()
            new_content = utils.get_room_content_from_db(self.current_room).replace(self.room_content, "")  # essentially take the difference of the most current string and the previous to find new messages
            if new_content != '':
                # add new_content to database
                cursor.execute("UPDATE rooms SET room_content=? WHERE room_name=?", (new_content, self.current_room,))
                cursor.execute("UPDATE rooms SET room_update=? WHERE room_name=?", ('1', self.current_room,))
                conn.commit()
                conn.close()

                # send new_content to parent process which will handle/print it
                return self.queue.put_nowait(new_content)

            conn.close()
            return


    def __aiter__(self):
        return self


if __name__ == "__main__":
    # __spec__ = None  # to avoid a stupid error raised when using pdb (https://stackoverflow.com/questions/45720153/python-multiprocessing-error-attributeerror-module-main-has-no-attribute/60922965?noredirect=1#comment83471090_45720872)
    # sys.excepthook = utils.excepthook_replacement
    
    current_user = None
    current_room = None

    app = ChatApp(current_user, current_room)
    asyncio.run(app.run())
