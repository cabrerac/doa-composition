# Set base image (host OS)
FROM python:3.8-slim-buster

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements-microservices.txt .

# Install any dependencies
RUN pip install -r requirements-microservices.txt

# Copy the microservice code to the working directory
COPY microservices/service_34_sync.py .

# Create logic directory
RUN mkdir ./logic

# Copy the util code to the working directory
COPY microservices/logic/util.py ./logic/

# Create description directory
RUN mkdir ./description

# Copy the service description
COPY datasets/descriptions/100-100000-services/services/service_34.json ./description/

# Specify the command to run on container start
CMD ["python", "./service_34_sync.py"]
