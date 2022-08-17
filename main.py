from deployment import deploy_to_aws
from clients import client
import time
import json
import microservices.logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer

# Approach
approaches = ['centralised', 'doa']
rabbit_credentials_file = 'rabbit-mq.yaml'

# Defining services to register and create in the AWS infrastructure
print('0. Defining services...')

home_service_sync = {
    'name': 'home-service-sync', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/home', 'priority': 1, 'count': 1
}

home_service_async = {
    'name': 'home-service-async', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/home', 'priority': 2, 'count': 1, 'topic': 'service.home'
}

add_service_sync = {
    'name': 'add-service-sync', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/add', 'priority': 3, 'count': 1
}

add_service_async = {
    'name': 'add-service-async', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/add', 'priority': 4, 'count': 1, 'topic': 'service.add'
}

square_service_sync = {
    'name': 'square-service-sync', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/square', 'priority': 5, 'count': 1
}

square_service_async = {
    'name': 'square-service-async', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/square', 'priority': 6, 'count': 1, 'topic': 'service.square'
}

services = [home_service_sync, home_service_async, add_service_sync, add_service_async, square_service_sync,
            square_service_async]

# Deploying AWS resources and services
print('1. Deploying services...')
external_url, rabbitmq_url = deploy_to_aws.deploy_services('templates/doa-resources-template.yml',
                                                           'templates/doa-service-template.yml',
                                                           './rabbit-mq.yaml', services)
print('Load Balancer URL: ' + external_url)
print('RabbitMQ Endpoint URL: ' + rabbitmq_url)


def callback(ch, method, properties, body):
    message = json.loads(body)
    res = message['res']
    print('Response: ' + res)


# A simple example of a centralised service composition that calculates the square of the addition of two numbers
def centralised_composition(s1, s2):
    parameters = {}
    home = client.make_request(external_url, home_service_sync['path'], parameters)
    print(home['res'])
    parameters = {'s1': s1, 's2': s2}
    addition = client.make_request(external_url, add_service_sync['path'], parameters)
    parameters = {'p': addition['res']}
    square = client.make_request(external_url, square_service_sync['path'], parameters)
    print('(' + str(s1) + ' + ' + str(s2) + ')^2 = ' + str(square['res']))


# A simple example of a doa-based service composition that calculates the square of the addition of two numbers
def doa_composition(s1, s2):
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)

    message_dict = {'user_topic': 'user.response', 'desc': 'request from main!!!', 'next_topic': 'user.response'}
    message_json = json.dumps(message_dict, indent=4)
    producer = Producer(credentials)
    producer.publish(home_service_async['topic'], message_json)
    consumer = Consumer(credentials, 'user.response', callback)

    message_dict = {
        'user_topic': 'user.response', 'desc': 'request from main!!!', 'next_topic': 'service.square',
        'parameters': [
            {'name': 's1', 'value': s1},
            {'name': 's2', 'value': s2}
        ]
    }
    message_json = json.dumps(message_dict, indent=4)
    producer = Producer(credentials)
    producer.publish(home_service_async['topic'], message_json)
    consumer = Consumer(credentials, 'user.response', callback)


time.sleep(10)
print('2. Executing compositions...')
for approach in approaches:
    print('### ' + approach + ' Approach ###')
    if approach == 'centralised':
        centralised_composition(4, 5)
    if approach == 'doa':
        doa_composition(4, 5)
