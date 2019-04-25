# Idea ACK: TJ Horner's Video Explination of Docker: https://www.youtube.com/watch?v=Y4WSnreOBbo
# Written by me
FROM python:3.7

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "/app/core.py"]