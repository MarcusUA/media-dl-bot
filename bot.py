import os
import yt_dlp
import telebot
from telebot.types import BotCommand, InputMediaVideo
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
FILENANE_TMPL = os.environ.get('FILENANE_TMPL')
if not FILENANE_TMPL:
    FILENANE_TMPL = '%(title)s [%(id)s].%(ext)s'


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


def request_dl(message, url):
    ydl_opts = {
        'outtmpl': f'{UPLOAD_FOLDER}/{FILENANE_TMPL}'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            #print(json.dumps(ydl.sanitize_info(info)))
            #video_title = info['title']
            #video_url = info['url']
            video_id = info['id']
            video_ext = info['ext']
            ydl.download([url])

            
            #bot.reply_to(message, "Successfully downloaded video, uploading...")
            vid_media = []
            with open(os.path.join(UPLOAD_FOLDER, f"{video_id}.{video_ext}"), 'rb') as fh:
                vid_data = fh.read()
                media = InputMediaVideo(vid_data)
                vid_media.append(media)
            bot.send_media_group(message.chat.id, vid_media)

        except Exception as e:
            print(f"Error downloading video: {e}")
            bot.reply_to(message, text="Failed to download the video.")


bot = telebot.TeleBot(BOT_TOKEN)

# Commands
MAIN_COMMANDS = [BotCommand(command='start', description='Start the Bot'),
                 BotCommand(command='help', description='Click for Help')]
bot.set_my_commands(MAIN_COMMANDS)

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
    """)


# Messages
@bot.message_handler(regexp='https://.+')
@verify_access()
def handle_message(message):
        url = message.text
        request_dl(message, url)

bot.infinity_polling()