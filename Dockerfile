FROM python:3.7-slim

RUN pip3 install --upgrade pip \
    && apt-get update \
    && apt-get -y install ffmpeg \
    && apt-get -y install sox

WORKDIR /auto_transcript

COPY . /auto_transcript

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]