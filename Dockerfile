FROM python:3.12-slim
ADD hitman_tg_bot /hitman_tg_bot
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 freeze
CMD python hitman_tg_bot/telegram_bot.py