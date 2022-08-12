# Set base image (host OS)
FROM python:3.8-slim-buster

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the rabbitMQ credentials to the working directory
COPY rabbit-mq.yaml .

# Copy the dependencies file to the working directory
COPY requirements-microservices.txt .

# Install any dependencies
RUN pip install -r requirements-microservices.txt

# Copy the microservice code to the working directory
COPY microservices/home.py .

# Create logic directory
RUN mkdir /app/logic

RUN pwd
RUN ls -la

# Copy the util code to the working directory
COPY microservices/logic/util.py ./logic/

# Copy the function code to the working directory
COPY microservices/logic/home_function.py ./logic/

RUN ls -la logic

# Specify the command to run on container start
CMD ["python", "./home.py"]

