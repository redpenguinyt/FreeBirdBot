FROM python:3.11.4-bookworm

WORKDIR /app

RUN apt update && apt install -y ffmpeg libffi-dev python3-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install PyNaCl

COPY . .

CMD [ "python3", "main.py" ]