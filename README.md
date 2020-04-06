# AWS IoT GreenGrass Tutorial

This is an [AWS IoT GreenGrass](https://aws.amazon.com/greengrass/) advanced tutorial for following use cases:
  - Deploying a web service using [Docker Application Deployment](https://docs.aws.amazon.com/greengrass/latest/developerguide/docker-app-connector.html) connector
  - Deploying a Lambda function in AWS IoT GreenGrass
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

### Setup EC2 instance for development
  - `ssh` into EC2 instance using the SSH key you used to launch the EC2 instance.
  - Run `.docker/arm-docker.sh` to install Docker engine on the development machine
  - Run `./docker/build-tools/build-and-deploy.sh <aws-region>` to
