# AWS IoT GreenGrass Tutorial

This is an [AWS IoT GreenGrass](https://aws.amazon.com/greengrass/) advanced tutorial for following use cases:
  - Deploying a web service using [Docker Application Deployment](https://docs.aws.amazon.com/greengrass/latest/developerguide/docker-app-connector.html) connector
  - Deploying an AWS IoT device using Docker Application Deployment coneector
  
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
  - `ssh` into EC2 instance using the SSH key you used to launch the EC2 instance.
  - `cd docker`
  - `./arm-docker.sh` to install Docker engine on the development machine
  - `cd container-hello-armv7`
  - `./build-tools/build-and-deploy.sh <aws-region>` to build hello world Docker image and ;push it to [Amazon ECR](https://aws.amazon.com/ecr/). Note the ECR URI for the Docker image. 
  - `cd ..`
  - Edit `docker-compose.yml` to set the ECR URI image for the web service. Comment out the `device` part. Your `docker-compose.yml` should look as follows:
  
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
  - Use [Docker Application Deployment Connector](https://docs.aws.amazon.com/greengrass/latest/developerguide/docker-app-connector.html) in your AWS IoT GreenGrass Group to deploy the hello world web service to the GreenGrass running on the Rspberry Pi
  - If your web service application is deployed successfully on the GreenGrass, you should be able to test the web service by using `curl` or a browser. For example, assuming Raspberry Pi hostname is `ggc`, you can do `curl http://ggc/` and you should see a JSON response:
  
   ```
   {"timestamp": 1586145890.1501749, "message": "Hello world!", "count": 1}
   
   ```
   Of course, the timestamp and the count will vary.
   
