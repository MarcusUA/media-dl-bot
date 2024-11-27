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
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
if UPLOAD_FOLDER:
     print (f"UPLOAD_FOLDER: {UPLOAD_FOLDER}")
     if not os.path.exists(UPLOAD_FOLDER):
        print (f"Folder doesn't exist trying to create.")
        os.makedirs(UPLOAD_FOLDER)


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

def extract_arg(arg):
    return arg.split()[1:]

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

def get_files_in_folder(dir):
    try:
        files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
        return files
    except:
        return ["Couldn't retrieve file list"]


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
        Available commands:
        /start
        /help
        /ls_dl - list downloaded files.
        /up <filename> - upload a file.
        /vid_up <filename> - upload a video.
    """)


@bot.message_handler(commands=['ls_dl'])
@verify_access()
def list_files(message):
    files = get_files_in_folder(UPLOAD_FOLDER)
    bot.reply_to(message, '\n'.join(files))


@bot.message_handler(commands=['up'])
@verify_access()
def upload_file(message):
    filename = " ".join(extract_arg(message.text))
    if filename:
        file = open(os.path.join(UPLOAD_FOLDER, filename), 'rb')
        bot.send_document(message.chat.id, file)
    else:
        bot.reply_to(message, "Please add a file name to upload")


@bot.message_handler(commands=['vid_up'])
@verify_access()
def upload_video(message):
    filename = " ".join(extract_arg(message.text))
    vid_media = []
    if filename:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as fh:
            vid_data = fh.read()
            media = telebot.types.InputMediaVideo(vid_data)
            vid_media.append(media)
        bot.send_media_group(message.chat.id, vid_media)
    else:
        bot.reply_to(message, "Please add a file name to upload")


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