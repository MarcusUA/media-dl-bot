import os
import requests
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
YTDL_URL = os.environ.get('YTDL_URL')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, f"Your UserID: {message.from_user.username}")

@bot.message_handler(regexp='https://.+')
def handle_message(message):
    try:
        url = message.text
        data = {
            "url": f"{url}", 
            "format": "bestvideo"
        }
        response = requests.post(YTDL_URL, data=data)
        print(response.status_code)
        print(response.content)
        bot.reply_to(message, "Successfully added to the download queue")
    except:
        bot.reply_to(message, "Couldn't add to the download queue, error occured :(")

bot.infinity_polling()