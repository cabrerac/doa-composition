from deployment import deploy_to_aws
from clients import client
import time
import microservices.logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer


# Approach
approaches = ['centralised', 'doa']
rabbit_credentials_file = 'rabbit-mq.yaml'
rt_metric = {}

# Defining services to register and create in the AWS infrastructure
print('0. Defining services...')

home_service_sync = {
    'name': 'home-service-sync', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/home', 'priority': 1, 'count': 1
}

home_service_async = {
    'name': 'home-service-async', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/home_async', 'priority': 2, 'count': 1, 'topic': 'service.home'
}

add_service_sync = {
    'name': 'add-service-sync', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/add', 'priority': 3, 'count': 1
}

add_service_async = {
    'name': 'add-service-async', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/add_async', 'priority': 4, 'count': 1, 'topic': 'service.add'
}

square_service_sync = {
    'name': 'square-service-sync', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/square', 'priority': 5, 'count': 1
}

square_service_async = {
    'name': 'square-service-async', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
    'path': '/doa_composition/square_async', 'priority': 6, 'count': 1, 'topic': 'service.square'
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
    req_id = message['req_id']
    print('Response DOA: ' + str(res))
    rt_metric[req_id]['response_time'] = int(round(time.time() * 1000))
    rt_metric[req_id]['total_time'] = rt_metric[req_id]['response_time'] - rt_metric[req_id]['request_time']
    print(rt_metric)


# A simple example of a centralised service composition that calculates the square of the addition of two numbers
def centralised_composition(s1, s2):
    time.sleep(5)
    req_id = 'cen_1'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    rt_metric[req_id] = rt_measurement
    parameters = {}
    home = client.make_request(external_url, home_service_sync['path'], parameters)
    print('Response Centralised: ' + home['res'])
    rt_metric[req_id]['response_time'] = int(round(time.time() * 1000))
    rt_metric[req_id]['total_time'] = rt_metric[req_id]['response_time'] - rt_metric[req_id]['request_time']

    time.sleep(5)
    req_id = 'cen_2'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    rt_metric[req_id] = rt_measurement
    parameters = {'s1': s1, 's2': s2}
    addition = client.make_request(external_url, add_service_sync['path'], parameters)
    parameters = {'p': addition['res']}
    square = client.make_request(external_url, square_service_sync['path'], parameters)
    print('Response Centralised: ' + home['res'])
    rt_metric[req_id]['response_time'] = int(round(time.time() * 1000))
    rt_metric[req_id]['total_time'] = rt_metric[req_id]['response_time'] - rt_metric[req_id]['request_time']
    print(rt_metric)


# A simple example of a doa-based service composition that calculates the square of the addition of two numbers
def doa_composition(a, b):
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    consumer_thread = Consumer(credentials, 'user.response', callback)
    consumer_thread.start()
    time.sleep(5)
    req_id = 'doa_1'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time':0}    
    rt_metric[req_id] = rt_measurement
    message_dict = {'req_id': req_id, 'user_topic': 'user.response', 'desc': 'request from main!!!',
                    'next_topic': 'user.response'}
    producer = Producer(credentials)
    rt_metric[req_id]['response_time'] = int(round(time.time() * 1000))
    rt_metric[req_id]['total_time'] = rt_metric[req_id]['response_time'] - rt_metric[req_id]['request_time']
    producer.publish(home_service_async['topic'], message_dict)

    time.sleep(5)
    req_id = 'doa_2'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    rt_metric[req_id] = rt_measurement
    message_dict = {'req_id': req_id, 'user_topic': 'user.response', 'desc': 'request from main!!!',
                    'next_topic': 'service.square',
                    'parameters': [{'name': 'a', 'value': a}, {'name': 'b', 'value': b}]}
    producer = Producer(credentials)
    rt_metric[req_id]['response_time'] = int(round(time.time() * 1000))
    rt_metric[req_id]['total_time'] = rt_metric[req_id]['response_time'] - rt_metric[req_id]['request_time']
    producer.publish(add_service_async['topic'], message_dict)


time.sleep(10)
print('2. Executing compositions...')
for approach in approaches:
    print('### ' + approach + ' Approach ###')
    if approach == 'centralised':
        centralised_composition(4, 5)
    if approach == 'doa':
        doa_composition(4, 5)
