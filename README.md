# AWS IoT GreenGrass Tutorial

This is an *advanced* tutorial on following [AWS IoT GreenGrass](https://aws.amazon.com/greengrass/) use cases:
  - Deploying a web service using [Docker Application Deployment](https://docs.aws.amazon.com/greengrass/latest/developerguide/docker-app-connector.html) connector
  - Deploying an AWS IoT device using Docker Application Deployment coneector

The tutorial does not detail every step, encourgaing the reader to explore the [Getting started with AWS IoT GreenGrass](https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-gs.html) and learn in that process.

This tutorial assumes GreenGrass core software version 1.10.

## Hardwware and OS requirements
 
- Raspberry Pi (Armv7) 32 GB kit
- [Raspbian Buster OS](https://www.raspberrypi.org/downloads/raspbian/)

## Install AWS IoT GreenGrass Core software
 
- [Set up Raspberry Pi](https://docs.aws.amazon.com/greengrass/latest/developerguide/setup-filter.rpi.html)
- [Install AWS IoT GreenGrass core software  on the Raspberry  device](https://docs.aws.amazon.com/greengrass/latest/developerguide/module2.html)
- [Install Docker engine and Docker Compose](raspi/install-docker-engine.sh) on Raspberry Pi
 
## Running a web service using Docker Application Deployment connector

### Launch EC2 instance for development
In this use case, we run a hello world web service in AWS IoT GreenGrass on Raspberry Pi (Armv7) using Docker Application Deployment Connector. For this use case, we need to build a Docker image for Armv7 architecture. Therefore, we need access to a developer machine based on Armv7 architecture. So let us [launch an Amazon EC2](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html) `a1.xlarge` instance using this [Amazon Machine Image](https://aws.amazon.com/marketplace/pp/Canonical-Group-Limited-Ubuntu-1604-LTS-Xenial-Arm/B07KTDC2HN), with 50 GB Amazon Elastic Block Store volume. Even though `a1.xlarge` instance is based on Arm64 architecture, it allows us to build Docker images for Armv7 architecture.

### Build Docker image for web service
  - `ssh` into development EC2 instance using the SSH key you used to launch the EC2 instance.
  - `sudo apt-get install -y git` to install `git` package
  - `git clone` this Github repository and `cd` to the local Git repository root directory
  - `cd docker`
  - `./arm-docker.sh` to install Docker engine on the development machine
  - `cd container-hello-armv7`
  - `./build-tools/build-and-deploy.sh <aws-region>` to build hello world Docker image and push it to [Amazon ECR](https://aws.amazon.com/ecr/). Note the Amazon ECR URI of the Docker image you just pushed. You will need it in the next step.
  - `cd ..`
  
### Configure Docker Compose file
Edit `docker-compose.yml` to set the ECR URI image you jsut noted above. Comment out the `device` part. Your `docker-compose.yml` should look as follows:
  
```
version: '3'
services:
  web:
    image: <ECR URI here>
    ports:
      - '80:5000'
  #device:
    #image:
```
### Deploy Docker Application Connector

Now that we have a Docker image pushed in the ECR and a `docker-compose.yml` defiend to run our web sevice container, we are ready to use the Docker Application Deployment Connector to deploy our web service to the AWS IoT GreenGrass. Conceptually, this involves following steps:

  - Copy the `docker-compose.yml` to some prefix in your [Amazon S3](https://aws.amazon.com/s3/) bucket
  - Configure [Docker Application Deployment Connector](https://docs.aws.amazon.com/greengrass/latest/developerguide/docker-app-connector.html) in your AWS IoT GreenGrass Group and deploy the GreenGrass Group
  - If your web service application is successfully deployed using Docker Application Deployment Connector, you should be able to test the web service running on your Raspberry Pi by using `curl` command, or a web browser. For example, assuming your Raspberry Pi hostname is `ggc`, you can do `curl http://ggc/` and you should see a JSON response:
  
   ```
   {"timestamp": 1586145890.1501749, "message": "Hello world!", "count": 1}
   
   ```
   Of course, the `timestamp` and the `count` will vary.
   
## Running an AWS IoT Device using Docker Application Deployment connector

In this example, we run an AWS IoT device that emulates a security gateway. This device is not a real security gateway. It is merely a skelton device.

This example is similar to the previous example except in this case instead of running a web service, we will run an AWS IoT device  inside a Docker container on the GreenGrass. This device will not be part of the GreenGrass group. This device will connect to the AWS IoT Core, not the GreenGrass endpoint. 

### Create AWS IoT Thing

Follow [Getting Started with AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html)  to create an AWS IoT Thing and configure it. You will need to download the Thing certifcate, private and public key files for the next step. You will also need to note the Thing name, and the Thing ednpoint.

### Build Docker image for AWS IoT device

This step assumes you have already installed Docker on the development machine, as described in previous steps.

  - `scp` Thing certifcate, private and public key files to the development EC2 instance sing the SSH key you used to launch the EC2 instance
  - `ssh` into development EC2 instance
  - `cd container-security-gateway-armv7`
  - Copy Thing certifcate, private and public key files under `device/thing/` folder and renaming the files as follows:
  ```
  thing-certificate.pem.crt
  thing-private.pem.key
  thing-public.pem.key
  ```
  - `cd device`
  - Using your favorite editor (`vi`) set the Thing name in `THING` and Thing endpoint in `ENDPOINT` (Do not run this script).
  - `cd ..`
  - `./build-tools/build-and-deploy.sh <aws-region>` to build AWS IoT Docker image and ;push it to [Amazon ECR](https://aws.amazon.com/ecr/). Note the ECR URI for the Docker image. 
  - `cd ..`
  
### Configure Docker Compose file
 Edit `docker-compose.yml` to set the ECR URI image you just built in the device part. Unomment the `device` part. Your `docker-compose.yml` should look as follows:
  
```
version: '3'
services:
  web:
    image: <Web service ECR URI here>
    ports:
      - '80:5000'
  device:
    image: <Device ECR URI here>
```
### Deploy Docker Application Connector

Now that we have `docker-compose.yml` updated to include both the web sevice and AWS IoT device applications, we are ready to redeploy the Docker Application Deployment Connector to run the web service and AWS IoT device applications on our AWS IoT GreenGrass. 

You can interact with this device in AWS IoT Core console through its [device shadow](https://docs.aws.amazon.com/iot/latest/developerguide/using-device-shadows.html) document, changing the `desired` state in the document and observing the `reported` state change in response. 

An example shadow document for testing is shown below:

```
{
  "desired": {
    "welcome": "hello",
    "alram": "arm"
  },
  "reported": {
    "welcome": "hello",
    "alram": "arm"
  }
}
```

```
{
  "desired": {
    "welcome": "bye",
    "alram": "disarm"
  },
  "reported": {
    "welcome": "bye",
    "alram": "disarm"
  }
}
```
