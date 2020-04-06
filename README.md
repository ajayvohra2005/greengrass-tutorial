# AWS IoT GreenGrass Tutorial

This is an *advanced* tutorial on following [AWS IoT GreenGrass](https://aws.amazon.com/greengrass/) use cases:
  - Running a `hello world` web service using [Docker Application Deployment](https://docs.aws.amazon.com/greengrass/latest/developerguide/docker-app-connector.html) connector
  - Running an AWS IoT device using Docker Application Deployment coneector
  - Running a Lambda function in GreenGrass that interacts with the `hello world` local web service

The tutorial does not detail every step, encourgaing the reader to explore the [Getting started with AWS IoT GreenGrass](https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-gs.html) modules and other AWS online documentation resources.

This tutorial assumes GreenGrass core software version 1.10.

## Hardwware and OS requirements
 
- Raspberry Pi (Armv7) 32 GB kit
- [Raspbian Buster OS](https://www.raspberrypi.org/downloads/raspbian/)

## Install AWS IoT GreenGrass Core software
 
- [Set up Raspberry Pi](https://docs.aws.amazon.com/greengrass/latest/developerguide/setup-filter.rpi.html)
- [Install AWS IoT GreenGrass core software  on the Raspberry  device](https://docs.aws.amazon.com/greengrass/latest/developerguide/module2.html)
- [Install Docker engine and Docker Compose](raspi/install-docker-engine.sh) on Raspberry Pi
 
## Running the hello world web service using Docker Application Deployment connector

### Launch EC2 instance for development
In this use case, we run a `hello world` web service in AWS IoT GreenGrass on Raspberry Pi (Armv7) using Docker Application Deployment Connector. For this use case, we need to build a Docker image for Armv7 architecture. Therefore, we need access to a developer machine based on Armv7 architecture. So let us [launch an Amazon EC2](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html) `a1.xlarge` instance using this [Amazon Machine Image](https://aws.amazon.com/marketplace/pp/Canonical-Group-Limited-Ubuntu-1604-LTS-Xenial-Arm/B07KTDC2HN), with 50 GB Amazon Elastic Block Store volume. Even though `a1.xlarge` instance is based on Arm64 architecture, it allows us to build Docker images for Armv7 architecture.

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
Edit [docker-compose.yml](docker/docker-compose.yml) to configure `web image` with the ECR URI you just noted above. Comment out the `device` part. Your `docker-compose.yml` should look as follows:
  
```
version: '3'
services:
  web:
    image: <web service ECR URI here>
    ports:
      - '80:5000'
  #device:
    #image:
```
### Deploy Docker Application Connector

Now that we have a Docker image pushed in the ECR and a `docker-compose.yml` defined to run our web sevice container, we are ready to use the Docker Application Deployment Connector to deploy our web service to the AWS IoT GreenGrass. Conceptually, this involves following steps:

  - Copy the `docker-compose.yml` to some prefix in your [Amazon S3](https://aws.amazon.com/s3/) bucket
  - Configure [Docker Application Deployment Connector](https://docs.aws.amazon.com/greengrass/latest/developerguide/docker-app-connector.html) in your AWS IoT GreenGrass Group and [deploy the GreenGrass Group](https://docs.aws.amazon.com/greengrass/latest/developerguide/deployments.html)
  - If the `hello world` web service application is successfully deployed using Docker Application Deployment Connector, you should be able to test the web service running on your Raspberry Pi by using `curl` command, or a web browser. For example, assuming your Raspberry Pi hostname is `ggc`, you can do `curl http://ggc/` and you should see a JSON response:
  
   ```
   {"timestamp": 1586145890.1501749, "message": "Hello world!", "count": 1}
   
   ```
   Of course, the `timestamp` and the `count` will vary.
   
## Running an AWS IoT Device using Docker Application Deployment connector

In this example, we run an AWS IoT device that emulates a security gateway.The Python code for this security gateway is in the [security_gateway.py](docker/container-security-gateway-armv7/device/security_gateway.py) file.

This example is similar to the previous example except in this case instead of running a web service, we will run an AWS IoT device  inside a Docker container on the GreenGrass. This device will connect to its endpoint in the AWS IoT cloud, not the local GreenGrass endpoint.  This device will *not* be part of any [AWS IoT GreenGrass Group](https://docs.aws.amazon.com/greengrass/latest/developerguide/what-is-gg.html).

### Create AWS IoT Thing

Follow [Getting Started with AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html)  to create an AWS IoT Thing and configure it. You will need to download the Thing certifcate, private and public key files for the next step. You will also need to note the Thing name, and the Thing ednpoint.

### Build Docker image for AWS IoT device

This step assumes you have already installed Docker on the development machine, as described in previous steps.

  - `scp` Thing certifcate, private and public key files to the development EC2 instance sing the SSH key you used to launch the EC2 instance
  - `ssh` into development EC2 instance
  - `cd container-security-gateway-armv7`
  - Copy Thing certifcate, private and public key files to `device/thing/` folder, renaming the files as follows:
  ```
  thing-certificate.pem.crt
  thing-private.pem.key
  thing-public.pem.key
  ```
  - `cd device`
  - Using your favorite editor (`vi`) set the Thing name in `THING` and Thing endpoint in `ENDPOINT` (Do not run this script). You will find this information in AWS IoT console.
  - `cd ..`
  - `./build-tools/build-and-deploy.sh <aws-region>` to build AWS IoT Docker image and ;push it to [Amazon ECR](https://aws.amazon.com/ecr/). Note the ECR URI for the Docker image. 
  - `cd ..`
  
### Configure Docker Compose file
 Edit `docker-compose.yml` to set the ECR URI image you just built in the `device image`. Uncomment the `device` part. Your `docker-compose.yml` should look as follows:
  
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

## Running a Lambda function in GreenGrass that interacts with local web service
In this example, we deploy an [AWS Lambda](https://aws.amazon.com/lambda/features/) function to the AWS IoT GreenGrass Group. We communicate with this Lambda function from the AWS IoT cloud by sending message to a named [AWS IoT Topic](https://docs.aws.amazon.com/iot/latest/developerguide/topics.html) 

The named AWS IoT topic is wired to the Lambda function using [AWS IoT GreenGrass Subscription](https://docs.aws.amazon.com/greengrass/latest/developerguide/config-lambda.html). The Lambda function makes a REST API request to the local `hello world` web service we dployed at the beginning of this tutorial. The Lambda function receives a JSON reponse frome the local web service, and uses the JSON to update its AWS IoT cloud shaodw document. The Lambda function is wired to the AWS IoT cloud shadow using GreenGrass subscription.

### Package and deploy the Lambda function in AWS Console

The Python code for the Lambda function is in [gg-hello-connector.py](lambda/gg-hello-connector/gg-hello-connector.py) file.
To package and deploy the Lambda function we execute following steps:

  - `cd lambda`
  - `./lambda-deployment.sh  gg-hello-connector requests greengrasssdk` to create a Lambda deployment package
  - `cd gg-hello-connector`
  -  `zip -g ../gg-hello-connector.zip  gg-hello-connector.py` to add the Python code file to the package
  - Use AWS management console to deploy the `gg-hello-connector.zip` package to create a new AWS Lambda function named `gg-hello-connector`
  - Publish the Lambda function as a new version
  - [Configure the Lambda function for the AWS IoT GreenGrass Group](https://docs.aws.amazon.com/greengrass/latest/developerguide/config-lambda.html)
  - [Configure AWS IoT GreenGrass subscription](https://docs.aws.amazon.com/greengrass/latest/developerguide/config-lambda.html) to connect a named AWS IoT cloud topic to the Lambda function
  - Configure AWS IoT GreenGrass subscription to connect Lambda function to its AWS IoT shadow topic
  
 ### Test Lambda function running in GreenGrass
 
 Using AWS IoT Console Test function, send any JSON message to the named AWS IoT topic you configured in the GreenGrass Group subscription in the previous step. 
 
 If the Lambda function is successfully running in the GreenGrass, when you send a JSON test message to Lambda funtion on the named topic, the GreenGrass Core shadow should get updated with a JSON `hello world` message, as shown in the example below:
```
{
  "desired": {
    "welcome": "aws-iot"
  },
  "reported": {
    "welcome": "aws-iot",
    "timestamp": 1585513082.9430707,
    "count": 2,
    "message": "Hello world!"
  }
}
```
