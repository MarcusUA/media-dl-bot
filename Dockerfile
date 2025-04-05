FROM python:3

ADD bot.py .

RUN apt-get update 
RUN apt-get install ffmpeg -y
RUN pip install pyTelegramBotAPI requests python-dotenv yt_dlp


CMD ["./bot.py"]
ENTRYPOINT ["python"]