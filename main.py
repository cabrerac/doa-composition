from deployment import deploy_to_aws
from clients import client
import time
import microservices.logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer

# Approach
approaches = ['doa']

# Defining services to register and create in the AWS infrastructure
print('0. Defining services...')

home_service_sync = {
    'name': 'doa-composition-home-service-sync-sync', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/home-sync', 'priority': 1, 'count': 1
}

home_service_async = {
    'name': 'doa-composition-home-service-sync-async', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/', 'priority': 1, 'count': 1, 'topic': 'service.home'
}

add_service = {
    'name': 'doa-composition-add-service', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/add', 'priority': 2, 'count': 1
}

square_service = {
    'name': 'doa-composition-square-service', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/square', 'priority': 3, 'count': 1
}
services = []

# Deploying AWS resources and services
print('1. Deploying services...')
external_url, rabbitmq_url = deploy_to_aws.deploy_services('templates/doa-resources-template.yml',
                                                           'templates/doa-service-template.yml',
                                                           './rabbit-mq.yaml', services)
print('Load Balancer URL: ' + external_url)
print('RabbitMQ Endpoint URL: ' + rabbitmq_url)


def callback(ch, method, properties, body):
    msg = body.decode()
    print('Received: ' + msg)


# A simple example of a centralised service composition that calculates the square of the addition of two numbers
def centralised_composition(s1, s2):
    parameters = {}
    home = client.make_request(external_url, home_service_sync['path'], parameters)
    print(home['res'])
    """parameters = {'s1': s1, 's2': s2}
    addition = client.make_request(external_url, add_service['path'], parameters)
    parameters = {'p': addition['res']}
    square = client.make_request(external_url, square_service['path'], parameters)
    print('(' + str(s1) + ' + ' + str(s2) + ')^2 = ' + str(square['res']))"""


# A simple example of a doa-based service composition that calculates the square of the addition of two numbers
def doa_composition(s1, s2):
    parameters = {}
    credentials = util.read_rabbit_credentials('rabbit-mq.yaml')
    producer = Producer(credentials)
    producer.publish(home_service_async['topic'], 'request from main!!!')
    consumer = Consumer(credentials, 'user.response', callback)
    """parameters = {'s1': s1, 's2': s2}
    addition = client.make_request(external_url, add_service['path'], parameters)
    parameters = {'p': addition['res']}
    square = client.make_request(external_url, square_service['path'], parameters)
    print('(' + str(s1) + ' + ' + str(s2) + ')^2 = ' + str(square['res']))"""


time.sleep(30)
print('2. Executing compositions...')
for approach in approaches:
    print('### ' + approach + ' Approach ###')
    if approach == 'centralised':
        centralised_composition(4, 5)
    if approach == 'doa':
        doa_composition(4, 5)

