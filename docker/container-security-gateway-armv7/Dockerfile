FROM armv7/armhf-ubuntu:16.04

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
  
RUN apt-get install -y wget
RUN apt-get install -y git

RUN cd /
RUN wget -O /root-CA.crt https://www.amazontrust.com/repository/AmazonRootCA1.pem
RUN git clone https://github.com/aws/aws-iot-device-sdk-python.git
RUN cd aws-iot-device-sdk-python && python setup.py install

COPY device/security_gateway.py /security_gateway.py
COPY device/start.sh /start.sh
COPY device/superior-recon /superior-recon
ENTRYPOINT ["/start.sh"]
