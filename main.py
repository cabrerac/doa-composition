import time
import json
import random
import os
import sys
import pandas as pd

from deployment import deploy_to_aws
from clients import client
from registry import data_access
import microservices.logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer
from baselines import backward_planning
from baselines import conversations
from datasets import generator


# experimental setup variables
metrics = {}
results = []
rabbit_credentials_file = 'rabbit-mq.yaml'
dataset_path = './datasets/descriptions/'
results_file = ''


# creates dataset
def create_dataset(path, n, r, le):
    if not os.path.exists(path + str(n) + '-services/'):
        print('- Creating services and requests...')
        generator.create_services_requests(n, r, le)
        print('- Creating services implementations...')
        generator.create_services(n)
    else:
        print('- Dataset already exists.')


# writes results file
def save(file_name, results, fmt):
    df = pd.DataFrame.from_dict(results)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', newline='', encoding=fmt) as f:
        df.to_csv(f, encoding=fmt, index=False, header=f.tell() == 0)


# defines services to register and deploy in the AWS infrastructure
def get_services(service_type, services_number):
    services = []
    i = 1
    while i <= services_number:
        file = open('./datasets/descriptions/' + str(services_number) + '-services/services/service_'+str(i)+'.json')
        service = json.load(file)
        service['name'] = service['name'] + '_' + service_type
        service['imageUrl'] = ''
        service['port'] = 5000
        service['cpu'] = 256
        service['memory'] = 512
        service['path'] = '/doa_composition/' + service['name']
        service['priority'] = i
        service['count'] = 1
        services.append(service)
        i = i + 1
    return services


# gets service request
def get_request(path, n, approach, length):
    if approach == 'doa' or approach == 'planning':
        approach = 'goal'
    path = path + str(n) + '-services/requests/' + approach + '/' + str(length) + '/'
    request_file = random.choice(os.listdir(path))
    request = json.load(open(path + request_file))
    return request


# callback function for the doa based composition
def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    print('Response DOA request: ' + req_id)
    print('Description: ' + message['desc'])
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    results.append(metrics[req_id])
    save(results_file, results, 'utf-8')


# doa based composition approach
def doa_composition(request, n):
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    consumer_thread = Consumer(credentials, 'user.response', callback)
    consumer_thread.start()
    time.sleep(5)
    req_id = 'doa_' + str(len(metrics) + 1)
    print('Request: ' + req_id + ' ::: ' + request['name'] )
    topic = 'service.' + request['inputs'][0]['name']
    expected_output = request['outputs'][0]['name']
    message_dict = {'req_id': req_id, 'expected_output': expected_output, 'user_topic': 'user.response',
                    'desc': 'request from main!!!'}
    producer = Producer(credentials)
    measurement = {'id': req_id, 'services': n, 'approach': 'doa','request_time': int(round(time.time() * 1000)),
                   'response_time': int(round(time.time() * 1000)), 'total_time': 0}
    metrics[req_id] = measurement
    producer.publish(topic, message_dict)


# conversation based composition approach
def conversation_composition(external_url, request, n):
    req_id = 'conversation_' + str(len(metrics) + 1)
    measurement = {'id': req_id, 'services': n, 'approach': 'conversation', 
                   'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = measurement
    plan = conversations.create_plan(request)
    tasks = plan['task']
    index = 1
    parameters = {'inputs': request['inputs']}
    while index <= len(tasks):
        task = tasks[index]
        service = task['services'][0]
        request = client.make_request(external_url, service['path'], parameters)
        parameters['inputs'] = request['outputs']
        index = index - 1
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[request['id']]['response_time'] - metrics[request['id']]['request_time']
    save(results_file, metrics, 'utf-8')


# planning based composition approach
def planning_composition(external_url, request):
    time.sleep(5)
    plan = backward_planning.create_plan(request)
    rt_measurement = {'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[request['id']] = rt_measurement
    services = plan['services']
    index = len(services)
    parameters = {'inputs': request['inputs']}
    while index >= 1:
        service = services[index]
        request = client.make_request(external_url, service['path'], parameters)
        parameters['inputs'] = request['outputs']
        index = index - 1
    metrics[request['id']]['response_time'] = int(round(time.time() * 1000))
    metrics[request['id']]['total_time'] = metrics[request['id']]['response_time'] - metrics[request['id']]['request_time']
    save(results_file, metrics, 'utf-8')


# main program that runs experiments
def main(parameters_file):

    # reading parameters file
    print('0. Reading experiment parameters...')
    file = open(parameters_file)
    parameters = json.load(file)
    approaches = parameters['approaches']
    max_length = parameters['max_length']
    lengths = parameters['lengths']
    services_number = parameters['services_number']
    requests_number = parameters['requests_number']
    experiment_requests = parameters['experiment_requests']
    global results_file
    results_file = parameters['results_file']

    # creating dataset for the experiment
    print('1. Creating experiment datasets...')
    create_dataset(dataset_path, services_number, requests_number, max_length)

    # deploying AWS resources
    print('2. Deploying resources...')
    external_url, rabbitmq_url = deploy_to_aws.deploy_resources('templates/doa-resources-template.yml',
                                                                './rabbit-mq.yaml')
    print('Load Balancer URL: ' + external_url)
    print('RabbitMQ Endpoint URL: ' + rabbitmq_url)
    print('3. Executing experiments...')
    for approach in approaches:
        print('### ' + approach + ' Approach ###')
        # deploying services on top of AWS resources
        if approach == 'doa':
            services = get_services('async', services_number)
        if approach == 'conversation' or approach == 'planning':
            services = get_services('sync', services_number)
            data_access.insert_services(services)
        print('4. Deploying services...')
        deploy_to_aws.deploy_services('templates/doa-service-template.yml', services)

        print('5. Requesting services...')
        time.sleep(10)
        for length in lengths:
            i = 1
            while i <= experiment_requests:
                request = get_request(dataset_path, services_number, approach, length)
                if approach == 'doa':
                    doa_composition(request, services_number)
                if approach == 'conversation':
                    conversation_composition(external_url, request, services_number)
                if approach == 'planning':
                    planning_composition(external_url, request, services_number)
                i = i + 1

        # removing services from AWS
        print('6. Removing services...')
        deploy_to_aws.remove_services(services)
        if approach == 'conversation' or approach == 'planning':
            data_access.remove_services()
    # removing AWS resources
    time.sleep(600)
    print('7. Removing resources...')
    deploy_to_aws.remove_resources()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Please provide the experiments parameters file path in the correct format...')
