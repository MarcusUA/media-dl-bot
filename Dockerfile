FROM python:3.9

ADD bot.py .

RUN pip install pyTelegramBotAPI


CMD ["./bot.py"]
ENTRYPOINT ["python"]