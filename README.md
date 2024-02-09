# chatroom_app.py
A CLI application that users can run to create, save, and switch between chatrooms.

"chatroom_app.py" is a very bare-bones implementation (requiring only one built-in library). Multiple users should be able to send messages in the same chatroom 
(but this program only creates one user by default). The program centers around three Python classes: 1) ChatApp; 2) SharedChat; and, 3) SpeechBubble. ChatApp handles 
the application's administrative tasks (like logging users in and sending them to chatrooms); SharedChat manages the chatrooms for each user; and SpeechBubble organizes 
and beautifies each message.

```ChatApp``` is the parent class of ```SharedChat```, and (in its ```rooms``` attribute) it contains a dictionary of all the chatroom names (dictionary keys) and the 
content (stored simply as strings) for each chatroom (the dictionary values). When a user sends a message in a chatroom, their instance of ```SharedChat``` updates the 
corresponding dictionary value in ```ChatApp.rooms```, and other instances use "asyncio" to periodically check ```ChatApp.rooms``` for updates. When ```ChatApp.rooms``` 
is updated, other ```SharedChat``` instances will retrieve the updated chat data. This ensures that even with multiple users, a chatroom remains synchronized for all users.

However, this program doesn't handle merge conflicts. ```SharedChat``` instances check for updates at one second intervals. If one instance wants to update a ```ChatApp.rooms``` 
dictionary value, but another instance has updated it in the previous one second (before the first ```SharedChat``` instance could retrieve the update), this program does not 
handle these conflicts. It seems like there are probably best practices for this. I would be very happy to look into this - do you want me to extend this program to handle merge 
conflicts too?

I would also love to implement code tests and perhaps a database feature? Currently, the user's username and password are saved to ```ChatApp.users``` dictionary, but they 
don't persist after the program stops running. Containing these in another file or a database would be a fairly easy way for these values to persist.

In addition, this program doesn't stop users from having duplicate usernames. In fact, when it associates ```SharedChat``` instances with users, it assumes there are no 
duplicate usernames. A more real-world solution would be to identify users (internally) by some hash (maybe of their username and the time/date of their account creation, 
for example). That would better ensure that users are uniquely identified internally. I would be very happy to implement this too?

# NOTE: Since "chatroom_app.py" only implements one user by default, I have not thoroughly tested the syncing feature for multiple users.

Tested on Python 3.9.16.

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
