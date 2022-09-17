# DOA-Based Composition

The goal of this project is to implement and experiment with services compositions based on Data-Oriented Architectures principles.

## Infrastructure and Services Deployment in AWS

One key element of this project is the automatic deployment of infrastructure resources and services in AWS using Cloud Formations. This automation enables a high experiments reproducibility. It looks for the deployment of services on AWS Fargate, hosted in a private subnet, but accessible via a public load balancer.

The automatic deployment is implemented in the `./deployment/deploy_to_aws.py` file which submits container images and Cloud Formations to AWS. 

There are two templates in the `./templates/` folder, which are used to create the resources cloud formation and the services cloud formations. The resources cloud formation is submitted once at the beginning of the experiments. A service cloud formation is submitted for each service defined in the `./main.py` file.

Each service requires a container image which must be defined by a docker file. The `./dockers/` folder should contain the docker file for each service we want to deploy. If a service requires a particular python module, you can add it to the `./requirements-microservices.txt` file.

The `./microservices` folder contains the actual implementation of each service  using Flask.

## Service Composition

Right now there is a simple and centralised service composition implemented in the `./main.py` file. It uses traditional requests to the deployed services using the code in the `./clients/client.py` file.

## How to run it?

You can run the code (i.e., deploying services defined in the `./main.py` file and execute a simple composition) using the following command: 

`python main.py`

Our code uses AWS credentials to log into AWS from console. These credetils can be conigured as context variables:

`export AWS_REGION=xxxx`

`export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

`export AWS_ACCESS_KEY_ID=xxxxxxxxxxxxxxxx`
