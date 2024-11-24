FROM python:3.9

ADD bot.py .

RUN pip install pyTelegramBotAPI requests


CMD ["./bot.py"]
ENTRYPOINT ["python"]