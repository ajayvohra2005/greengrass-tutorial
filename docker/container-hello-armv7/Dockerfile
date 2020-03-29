FROM armv7/armhf-ubuntu:16.04

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
  
RUN pip install flask
COPY code/app.py /app.py
ENTRYPOINT ["python", "/app.py"]
