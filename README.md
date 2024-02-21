# chatroom_app.py
A CLI application that users can run to create, save, and switch between chatrooms.

The "Basic" folder contains a very bare-bones implementation (requiring only one built-in library). Multiple users are able to send messages in the same chatroom. The program centers around three Python classes: 1) ChatApp; 2) SharedChat; and, 3) SpeechBubble. ChatApp handles 
the application's administrative tasks (like logging users in and sending them to chatrooms); SharedChat manages the chatrooms for each user; and SpeechBubble organizes 
and beautifies each message. The "Basic" version is short, sweet, and I like to think (relatively) elegant.

The "Advanced" folder implements a more sophisticated chat room. While the ChatApp and SharedClass are similar, the advanced version stores usernames, passwords, and chat room data in a ```sqlite3``` database. The classes and methods are tailored to work with this database (compard to a simple dictionary in the "Basic" program). The database is self-contained in the file: the program creates the database if it does not already exist in the program's working directory, or simply accesses on if it exists. This enables the program to be run in multiple terminal sessions and communicate via the database.

The "Advanced" program uses asynchronous IO, which enables users to see chat updates while they are typing. Python's built-in "input()" function "blocks," which essentially means that when a user types a long message, the program waits for them to finish typing before continuing. In this application, that would mean that while a user is typing, their chat would not update with other users' messages. Using asynchronous IO enables users' chats to update while they are typing.

In addition, the "Advanced" program creates a child process which checks the database at one second intervals to see whether _other_ users have uploaded messages to the database. If so, the child process tells the main process to retrieve those messages. This is how users' chat applications stay apprised of other users.

Running the checker function in a child process prevents the main process (and consequently, the chat room from potentially becoming unresponsive. The checker function is resource intensive, and its resource intensity grows as other users' messages grow in size and frequency. If run in the main process, it could frequently make the chat room unresponsive, which would conflict with the requirements of a chat application. Chat applications should be prepared to accept users' input at all times. They should also quickly communicate a user's  message to other users. Running it in a child process could prevent the parent process (and consequently, the chat room) from becoming unresponsive.

One awkward feature is that due to a previously-reported bug in a core ```asyncio``` function (https://stackoverflow.com/questions/69997653/python-asyncio-gather-does-not-exit-after-task-complete), the "Advanced" program keeps updating the terminal window after the chat room is closed. This prevents users from switching between chat rooms. The easiest way I have found around this is simply to quit the program and run it again to join another chat room. In addition, while the checker function (referred to in the paragraphs above) runs, it updates the terminal window. If a users is typing, their words appear to disappear every second (the checker function refreshes every second). However, when the user "sends" their message, it appears in full in the chat. I believe this is due to the asynchronous nature of the function that accepts CLI user input ("ainput()" - an asynchronous implementation of the built-in "input()" function from the third-party package ```aioconsole```). "ainput" executes for a short period of time, then lets other code (such as that which updates the chat) execute, then executes for another short period of time. The CLI appears to be refreshed every time "ainput" releases and regains code execution, but the function caches "draft input." The program behaves as expected, but I imagine that one or two small changes to the third-party package ```aioconsole``` would allow users to see all of their "draft input" every time "ainput" releases and regains code execution.

I'm planning to implement code tests for this program. In addition, this program doesn't stop users from having duplicate usernames. In fact, when it associates ```SharedChat``` instances with users, it assumes there are no  duplicate usernames. A more real-world solution would be to identify users (internally) by some hash (maybe of their username and the time/date of their account creation, for example). That would better ensure that users are uniquely identified internally. I'm planning to implement this too!

The basic version was tested on Python 3.9.16. The advanced version was tested on Python 3.10.13.

# Examples

<img width="559" alt="Screenshot 2024-02-09 at 1 56 14 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/89463edf-08f9-44e6-b838-daa4b59863cd">

<img width="383" alt="Screenshot 2024-02-09 at 1 56 37 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/44b96ddf-4ae0-4cb9-ab3b-dda029b28202">

<img width="380" alt="Screenshot 2024-02-09 at 1 57 04 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/593cb454-db94-40f1-b84f-d131960467a2">

<img width="449" alt="Screenshot 2024-02-09 at 1 57 31 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/9721e270-6eff-4994-9e25-79c3de6b2202">

<img width="446" alt="Screenshot 2024-02-09 at 1 58 10 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/e3af6a32-b1b7-49d8-bb5a-9a4687624b71">

# Now we create another user in a different terminal session

<img width="452" alt="Screenshot 2024-02-09 at 1 59 19 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/9bfa7cf9-b92e-42f4-94ea-0dccec68f624">

<img width="443" alt="Screenshot 2024-02-09 at 1 59 46 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/1bbb0691-fb33-40eb-a46d-e1a941fc3bca">

<img width="405" alt="Screenshot 2024-02-09 at 2 01 18 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/0a0bd426-db77-451e-95eb-08a3c1c80d16">

# Meanwhile, back in the other terminal session...

<img width="294" alt="Screenshot 2024-02-09 at 2 01 58 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/2eb38ecb-1bd8-434c-8f20-55a915baf10f">

<img width="592" alt="Screenshot 2024-02-09 at 2 02 29 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/80b0878b-f1b7-47a8-bb80-36d1d17ceffa">

<img width="520" alt="Screenshot 2024-02-09 at 2 03 06 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/3090f7d9-16a2-4546-a3dc-8b8e762500a7">

# 'q' helps us exit chat rooms

<img width="394" alt="Screenshot 2024-02-09 at 2 03 39 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/3979f696-a7a2-4ddb-b87f-c7b001be5e07">

# We can log back in and our chat history is saved

<img width="462" alt="Screenshot 2024-02-09 at 2 05 19 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/ea1ad95c-da79-4bdc-b639-a253a097b99a">

<img width="510" alt="Screenshot 2024-02-09 at 2 05 53 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/10212e0d-3330-4dc8-80ab-8177bb533941">
