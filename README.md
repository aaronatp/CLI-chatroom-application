# chatroom_app.py
A CLI application that users can run to create, save, and switch between chatrooms.

"chatroom_app.py" is a very bare-bones implementation (requiring only one built-in library). Multiple users should be able to send messages in the same chatroom (but this program only creates one user by default). The program centers around three Python classes: 1) ChatApp; 2) SharedChat; and, 3) SpeechBubble. ChatApp handles the application's administrative tasks (like logging users in and sending them to chatrooms); SharedChat manages the chatrooms for each user; and SpeechBubble organizes and beautifies each message.

```ChatApp``` is the parent class of ```SharedChat```, and (in its ```rooms``` attribute) it contains a dictionary of all the chatroom names (dictionary keys) and the content (stored simply as strings) for each chatroom (the dictionary values). When a user sends a message in a chatroom, their instance of ```SharedChat``` updates the corresponding dictionary value in ```ChatApp.rooms```, and other instances use "asyncio" to periodically check ```ChatApp.rooms``` for updates. When ```ChatApp.rooms``` is updated, other ```SharedChat``` instances will retrieve the updated chat data. This ensures that even with multiple users, a chatroom remains synchronized for all users.

However, this program doesn't handle merge conflicts. ```SharedChat``` instances check for updates at one second intervals. If one instance wants to update a ```ChatApp.rooms``` dictionary value, but another instance has updated it in the previous one second (before the first ```SharedChat``` instance could retrieve the update), this program does not handle these conflicts. It seems like there are probably best practices for this. I would be very happy to look into this - do you want me to extend this program to handle merge conflicts too?

I would also love to implement code tests and perhaps a database feature? Currently, the user's username and password are saved to ```ChatApp.users``` dictionary, but they don't persist after the program stops running. Containing these in another file or a database would be a fairly easy way for these values to persist.

In addition, this program doesn't stop users from having duplicate usernames. In fact, when it associates ```SharedChat``` instances with users, it assumes there are no duplicate usernames. A more real-world solution would be to identify users (internally) by some hash (maybe of their username and the time/date of their account creation, for example). That would better ensure that users are uniquely identified internally. I would be very happy to implement this too?

# NOTE: Since "chatroom_app.py" only implements one user by default, I have not thoroughly tested the syncing feature for multiple users.

Tested on Python 3.9.16.
