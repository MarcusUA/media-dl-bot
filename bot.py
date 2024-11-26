import os
import requests
import telebot
from functools import wraps
from dotenv import load_dotenv



# configuration
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
print (f"BOT_TOKEN: {BOT_TOKEN}")
YTDL_URL = os.environ.get('YTDL_URL')
print (f"YTDL_URL: {YTDL_URL}")
USERS = os.environ.get('USERS')
if USERS:
    ALLOWED_USERS=USERS.split(",")


# functions

def is_allowed_username(username):
    if not USERS:
         return True
    return username in ALLOWED_USERS

def verify_access():
    def handler_restict(f):
        @wraps(f)
        def f_restrict(message, *args, **kwargs):
            username=message.from_user.username
            if is_allowed_username(username):
                return f(message, *args, **kwargs)
            else:
                print (f"Unknown user: {username}")
                bot.reply_to(message, f"Unregistered username: {username}")
        return f_restrict
    return handler_restict

def request_dl(url, format="best"):
    try:
        data = {
            "url": f"{url}", 
            "format": format
        }
        response = requests.post(YTDL_URL, data=data)
        print(f"requesting: {YTDL_URL}, data={data}")
        print(response.content)
        return True
    except:
        return False



bot = telebot.TeleBot(BOT_TOKEN)

# Commands

@bot.message_handler(commands=['start'])
@verify_access()
def send_welcome(message):
    bot.reply_to(message, f"Welcome {message.from_user.username}.\nSend me a Video URL to iniate download.\nSend /help for more info.")

@bot.message_handler(commands=['help'])
@verify_access()
def send_help(message):
    bot.reply_to(message, """Send me a Video URL to iniate download.
        Awailable commands:
        /start
        /help
    """)


# Messages
@bot.message_handler(regexp='https://.+')
@verify_access()
def handle_message(message):
        url = message.text
        if request_dl(url):
            bot.reply_to(message, "Successfully added to the download queue")
        else:
            bot.reply_to(message, "Couldn't add to the download queue, error occured :(")


bot.infinity_polling()