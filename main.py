import time
import json
import random
import os

from deployment import deploy_to_aws
from clients import client
from registry import data_access
import microservices.logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer


# Experimental setup
approaches = ['doa']
lengths = [1]
services_number = 100
requests_number = 10
metrics = {}
rabbit_credentials_file = 'rabbit-mq.yaml'


# Write results file
def save(file_name, results, fmt):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'a', newline='', encoding=fmt) as f:
        results.to_csv(f, encoding=fmt, index=False, header=f.tell() == 0)


# Defining services to register and deploy in the AWS infrastructure
def get_services(service_type):
    services = []
    i = 1
    while i <= services_number:
        file = open('./descriptions/services/service_'+str(i)+'.json')
        service = json.load(file)
        service['name'] = service['name'] + service_type
        service['imageUrl'] = ''
        service['port'] = 5000
        service['cpu'] = 256
        service['memory'] = 512
        service['path'] = 'doa_composition/' + service['name']
        service['priority'] = i
        service['count'] = 1
        services.append(service)
        i = i + 1
    return services


# Get service request
def get_request(approach, length):
    path = './descriptions/requests/' + approach + '/' + str(length)
    request = random.choice(os.listdir(path))
    return request


# Callback function for the doa-based composition
def callback(ch, method, properties, body):
    message = json.loads(body)
    res = message['res']
    req_id = message['req_id']
    print('Response DOA: ' + str(res))
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    save('results.csv', metrics, 'utf-8')
    print(metrics)


# A simple example of a doa-based service composition that calculates the square of the addition of two numbers
def doa_composition(request):
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    consumer_thread = Consumer(credentials, 'user.response', callback)
    consumer_thread.start()
    time.sleep(5)
    req_id = 'doa_' + len(metrics)
    print('Request: ' + req_id)
    topic = 'service.' + request['inputs'][0]['name']
    expected_output = request['outputs'][0]['name']
    message_dict = {'req_id': req_id, 'expected_output': expected_output, 'user_topic': 'user.response',
                    'desc': 'request from main!!!'}
    producer = Producer(credentials)
    measurement = {'id': req_id, 'approach': 'doa','request_time': int(round(time.time() * 1000)),
                   'response_time': int(round(time.time() * 1000)), 'total_time': 0}
    metrics[req_id] = measurement
    producer.publish(topic, message_dict)


# A simple example of a centralised service composition that calculates the square of the addition of two numbers
def conversation_composition(external_url, request):
    time.sleep(5)
    """req_id = 'cen_1'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = rt_measurement
    parameters = {}
    home = client.make_request(external_url, home_service_sync['path'], parameters)
    print('Response Centralised: ' + home['res'])
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']

    time.sleep(5)
    req_id = 'cen_2'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = rt_measurement
    parameters = {'s1': s1, 's2': s2}
    addition = client.make_request(external_url, add_service_sync['path'], parameters)
    parameters = {'p': addition['res']}
    square = client.make_request(external_url, square_service_sync['path'], parameters)
    print('Response Centralised: ' + home['res'])
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    print(metrics)"""


# A simple example of a centralised service composition that calculates the square of the addition of two numbers
def planning_composition(external_url, request):
    time.sleep(5)
    """req_id = 'cen_1'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = rt_measurement
    parameters = {}
    home = client.make_request(external_url, home_service_sync['path'], parameters)
    print('Response Centralised: ' + home['res'])
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']

    time.sleep(5)
    req_id = 'cen_2'
    print('Request: ' + req_id)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = rt_measurement
    parameters = {'s1': s1, 's2': s2}
    addition = client.make_request(external_url, add_service_sync['path'], parameters)
    parameters = {'p': addition['res']}
    square = client.make_request(external_url, square_service_sync['path'], parameters)
    print('Response Centralised: ' + home['res'])
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    print(metrics)"""


def main():
    # Deploying AWS resources
    print('0. Deploying resources...')
    external_url, rabbitmq_url = deploy_to_aws.deploy_resources('templates/doa-resources-template.yml',
                                                                './rabbit-mq.yaml')
    print('Load Balancer URL: ' + external_url)
    print('RabbitMQ Endpoint URL: ' + rabbitmq_url)
    print('1. Executing experiments...')
    for approach in approaches:
        print('### ' + approach + ' Approach ###')

        # Deploying services on top of AWS resources
        if approach == 'doa':
            services = get_services('async')
        if approach == 'conversation' or approach == 'planning':
            services = get_services('sync')
            data_access.insert_services(services)

        print('2. Deploying services...')
        deploy_to_aws.deploy_services('templates/doa-service-template.yml', services)

        print('3. Requesting services...')
        time.sleep(10)
        for length in lengths:
            i = 1
            while i <= requests_number:
                request = get_request(approach, length)
                if approach == 'doa':
                    doa_composition(request)
                if approach == 'conversation':
                    conversation_composition(external_url, request)
                if approach == 'planning':
                    planning_composition(external_url, request)
                i = i + 1

        # Removing services from AWS
        print('4. Removing services...')
        deploy_to_aws.remove_services('templates/doa-service-template.yml', services)
        if approach == 'conversation' or approach == 'planning':
            data_access.remove_services(services)
    # Removing AWS resources
    time.sleep(300)
    print('5. Removing resources...')
    deploy_to_aws.remove_resources('templates/doa-resources-template.yml', './rabbit-mq.yaml')


main()
