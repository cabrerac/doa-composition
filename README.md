# DOA-Based Composition

The goal of this project is to implement and experiment with services compositions based on Data-Oriented Architectures principles.

## Infrastructure and Services Deployment in AWS

One key element of this project is the automatic deployment of infrastructure resources and services in AWS using Cloud Formations. This automation enables experiments reproducibility. For more details on the automatic deployment please have a look to the [README file here](https://github.com/cabrerac/doa-composition/tree/main/deployment). 

## Services Dataset

Experiments use generated datasets of services which include service descriptions, service implementations using the Flask framework, and service requests. For more details on the datasets generation please have a look to the [README file here](https://github.com/cabrerac/doa-composition/tree/main/datasets). 

## Service Composition

The main file in this project orchestrates the automatic deployment of AWS resources, and services, as well as the datasets creation and the experiemnts execution. A different dataset can be created for each experiment. The configurations of the experiments can be found in the folder `./experiments/` and right now experiments can vary the approaches to evaluate, the length of the composition graphs, the services to register, the requests to generate, and the requests per experiment (i.e., respetitions).

# How to run it?

The following instructions were tested on the Windows Subsystem for Linux ([WSL](https://docs.microsoft.com/en-us/windows/wsl/install)) and an Ubuntu machine with Python 3.8.

1. Clone this repository

```
git clone https://github.com/cabrerac/doa-composition.git
```
```
cd doa-composition/
```

2. Create and activate virtual environment 

```
python3 -m venv venv
```
```
source venv/bin/activate
```

3. Install requirements

```
pip install  -r requirements.txt
```

4. Run the main passing the experiments parameters file. For example:

```
python main.py ./experiments/100_10000_services.json
```

The code uses AWS credentials to log into AWS from console. These credetils can be conigured as context variables:

`export AWS_REGION=xxxx`

`export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

`export AWS_ACCESS_KEY_ID=xxxxxxxxxxxxxxxx`
