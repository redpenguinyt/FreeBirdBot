FROM python:3.11.4-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN apt update && apt install -y ffmpeg

CMD [ "python3", "main.py" ]