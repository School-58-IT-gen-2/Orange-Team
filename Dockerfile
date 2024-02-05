FROM python:3.12-slim
ADD hitman /hitman
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 freeze
CMD python hitman/game.py