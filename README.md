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

<img width="513" alt="Screenshot 2024-02-04 at 2 20 53 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/3cdd9d10-c98d-4eb6-b94a-2604683a877b">

<img width="508" alt="Screenshot 2024-02-04 at 2 21 43 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/03b2656a-1d4f-46c7-842c-9dc124e71175">

<img width="502" alt="Screenshot 2024-02-04 at 2 22 15 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/644e1253-1332-4583-aa20-cd5b0aad3b29">

<img width="465" alt="Screenshot 2024-02-04 at 2 23 38 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/2d2a103a-7ca4-41f0-a883-de93f2433ead">

<img width="378" alt="Screenshot 2024-02-04 at 2 24 30 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/8790bcf6-ff8f-4b19-9eac-1feaec20fe76">

<img width="447" alt="Screenshot 2024-02-04 at 2 26 09 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/3ec661a9-c87e-45ab-86b0-5a28e7f7b6a6">

<img width="384" alt="Screenshot 2024-02-04 at 2 26 50 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/f318c6ed-6a70-4158-accb-30bf6663b205">

NOTE: Once we have created multiple chats, we can switch between them and the chat history is saved.

<img width="652" alt="Screenshot 2024-02-04 at 2 27 23 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/fdbb4131-1541-495c-9100-86ba7b65e8fc">

<img width="665" alt="Screenshot 2024-02-04 at 2 28 36 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/60a2ca36-3027-4abe-8293-374c97c86ab7">

<img width="383" alt="Screenshot 2024-02-04 at 2 29 12 AM" src="https://github.com/aaronatp/CLI-chatroom-application/assets/58194911/1478d72f-95f8-48bb-be55-f4396a57f728">


