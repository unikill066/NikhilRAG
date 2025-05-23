# pip install firebase-admin
import firebase_admin, pyrebase
from firebase_admin import credentials
from firebase_admin import database

cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-database-url.firebaseio.com'
})
def create_message(user_id, username, message_text):
    return {
        'user_id': user_id,
        'username': username,
        'text': message_text,
        'timestamp': firebase_admin.db.ServerValue.TIMESTAMP
    }
def send_message(chat_id, user_id, username, message_text):
    chat_ref = db.reference(f'/chats/{chat_id}/messages')
    message = create_message(user_id, username, message_text)
    new_message_ref = chat_ref.push(message)
    db.reference(f'/chats/{chat_id}').update({
        'lastMessage': message_text,
        'lastMessageTimestamp': message['timestamp']})
    
    return new_message_ref.key
def get_all_messages(chat_id):
    messages_ref = db.reference(f'/chats/{chat_id}/messages')
    return messages_ref.get()

config = {"apiKey": "your-api-key",
    "authDomain": "your-project.firebaseapp.com",
    "databaseURL": "https://your-database-url.firebaseio.com",
    "storageBucket": "your-project.appspot.com"}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def stream_handler(message):
    print(message["data"])