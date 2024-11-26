FROM python:3

ADD bot.py .

RUN pip install pyTelegramBotAPI requests python-dotenv


CMD ["./bot.py"]
ENTRYPOINT ["python"]