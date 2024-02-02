import asyncio


class ChatApp:
    """
    We initialize a class instance in 'if __name__ == "__main__":', look there for more information.
    """
    def __init__(self, users, rooms, current_user, current_room):
        self.users = users
        self.rooms = rooms
        self.current_user = current_user
        self.current_room = current_room

    def ensure_logged_in(self):
        '''
        Before users can access a chatroom, we make sure they are logged in.

        If they're not, we ask them to log in or create an account.
        '''
        if self.current_user in self.users:
            return True
        
        while True:
            print("Do you have an account or do you want to create one?\n\na) Log in to my account\nb) Create account\n\n")
            answer = input("> ").lower()  # Convert input to lowercase for case-insensitive comparison

            if answer == 'a':
                if self.log_in():
                    return True  # Exit the loop if login is successful
            elif answer == 'b':
                if self.create_account_and_log_in():
                    return True # Exit the loop if account creation is successful
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
            
            if username not in self.users:
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
                
                elif password != self.users[username]:
                    print("Incorrect password!\n")
                    continue

                self.users[username] = password
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
        self.users[username] = password
        self.current_user = username

        return True
        

    def get_chat_room(self):
        """
        Gets chatroom for user. Users can either access an existing one, or create a new one.

        This method leaves creation/joining chatrooms to callees.
        """
        print("Congratulations on logging in!")

        while True:
            print("Press 'a' to join a shared chat room or 'b' to create your own")
            response = input("> ")
            if response == 'a':
                return self.join_room()  # after this function returns, by default we prepare to end the program
            elif response == 'b':
                response = self.create_room()
                continue
            else:
                print(f"Invalid choice: \"{response}\"")
                continue


    def create_room(self):
        """
        This function only creates the room.
        
        It leaves it to the 'join_room' method to actually initialize and join the room.
        """
        while True:
            print("What is the name of the chat room you want to create?")
            print("Press 'q' to return to the main menu")
            response = input("> ")
            if response == 'q':
                return False
            
            if response in self.rooms.keys():
                print(f"{response} already exists. Do you want to return to the main menu to join it?")
                answer = input("> ")
                if answer == 'yes':
                    return
                elif answer == 'no':
                    print("ok!")
                    continue
                else:
                    print("Please write 'yes' or 'no'!\n")
                    continue

            self.rooms[response] = ''  # we're going to store the room's message content in the dict value
            print(f"Congratulations! You've created room {response}")

            return


    async def join_room(self):
        """
        Joins a chatroom and when there is data from one of them,
        this function updates the ChatApp.rooms attribute (essentially
        it updates/stores the content associated with the chatroom).
        """
        while True:
            print("What is the name of the room you would like to join?")
            print("Press 'q' to return to the main menu")
            response = input("> ")

            if response == 'q':
                return False
            
            elif response not in self.rooms.keys():
                print("Room doesn't exist!\n")
                print("If you would like to create the room, please return to the main menu")
                continue

            else:
                chatroom = SharedChat(self.users, self.rooms, self.current_user, response)
                # result = await chatroom.join_chat(self.current_user, response, self)
                # await ... yields the chatroom content which we send to the parent class instance,
                # allows other users to access and contribute content in a relative data-safe way
                async for result in chatroom.join_chat(self.current_user, response, self):
                    if result is not None:
                        self.rooms[response] = result


    async def run(self):
        while True:
            self.ensure_logged_in()
            await self.get_chat_room()  

            while True:
                print("Do you want to log off? (yes/no)")
                answer = input("> ").lower()
                if answer == 'yes':
                    self.current_user = None
                    self.current_room = None
                    print("Goodbye!")
                    return
                
                elif answer == 'no':
                    break

                else:
                    print("\nPlease answer 'yes' or 'no'!")


class SharedChat(ChatApp):
    """
    Look at the comments at the start of the program for general
    details about this class' function/position in the program
    
    This class manages chat "instances." Each user/room is an instance.
    Different users in the same room access the chat through different
    SharedChat instances.
    """
    def __init__(self, users, rooms, current_user, room, parent=None):
        super().__init__(users, rooms, current_user, current_room)
        self.current_room = room  # note, we override the parent class' self.current_method
        self.parent = parent


    async def join_chat(self, current_user: str, room: str, parent: ChatApp):
        """
        User types messages here. This function also periodically check whether other users have
        added to the chat, and if so, this method fetches the "updated" chat.
        
        This method delegates to the SpeechBubble class to beautify the messages.

        Caller performs error checking for the room name.
        """
        ostream = parent.rooms[room]  # Retrieves chat data - chat data stored in parent
        if ostream == '':
            print(f"Congratulations on joining {room}!")
            print("Send a message!")

        else:
            print(ostream)  # we print the chat history if it's not empty

        print("Press 'q' to leave")

        async def check_room_updates(ostream: str, room: str, chat_length: int, parent: ChatApp):
            while True:
                await asyncio.sleep(1)  # Check every second
                if len(ostream) != chat_length:  # low-cost way of checking whether e.g., someone else has contributed to the chat
                    ostream = parent.rooms[room]  # Get potential updates
                    chat_length = len(ostream)

        chat_length = len(ostream)
        asyncio.create_task(check_room_updates(ostream, room, chat_length, parent))

        while True:
            message = input("> ")
            if message == 'q':
                break

            bubble = SpeechBubble(current_user, message)
            yield parent.rooms[room] + bubble.beautify()  # yields back to the caller and also prints message


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


    def beautify(self):
        top = "-" * self.line_length
        bottom = "-" * self.line_length
        body = f"| {self.wrap_multi_line(self.username, self.text)} |"
        print(top)
        print(body)
        print(bottom)
        return top + "\n" + bottom + "\n" + body


if __name__ == "__main__":
    # in reality, these variables would probably be stored in other files or a database etc.
    # I have initialized them here for the sake of keeping this program self-contained
    users = {'aaron': 'password', 'ari': 'other password'}  # dictionary for storing users and passwords
    rooms = {}  # associates rooms with room-content (e.g., messages, etc.)
    current_user = None
    current_room = None

    app = ChatApp(users, rooms, current_user, current_room)
    asyncio.run(app.run())
