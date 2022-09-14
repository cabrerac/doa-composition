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
def create_dataset(experiment, path, n, r, le):
    if not os.path.exists(path + str(n) + '-services/'):
        print('- Creating services and requests...')
        generator.create_services_requests(n, r, le)
        print('- Creating services implementations...')
        generator.create_services(experiment, n)
    else:
        print('- Dataset already exists.')


# writes results file
def save(file_name, results, fmt):
    df = pd.DataFrame.from_dict(results)
    df.drop(columns=['request_time', 'response_time'])
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', newline='', encoding=fmt) as f:
        df.to_csv(f, encoding=fmt, index=False, header=f.tell() == 0)


# defines services to register and deploy in the AWS infrastructure
def get_services(service_type, services_number, priority):
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
        service['priority'] = priority
        service['count'] = 1
        services.append(service)
        priority = priority + 1
        i = i + 1
    return services


# gets service request
def get_requests(path, n, length):
    requests = {}
    approach = 'goal'
    path = path + str(n) + '-services/requests/' + approach + '/' + str(length) + '/'
    request_file = random.choice(os.listdir(path))
    requests['goal'] = json.load(open(path + request_file))
    path = path.replace('/goal/','/conversation/')
    requests['conversation'] = json.load(open(path + request_file))
    return requests


# callback function for the doa based composition
def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    print('Response DOA request: ' + req_id)
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    results.append(metrics[req_id])
    save(results_file, results, 'utf-8')


# doa based rabbit consumer
def rabbit_doa_consumer():
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    consumer_thread = Consumer(credentials, 'user.response', callback)
    consumer_thread.start()
    time.sleep(10)


# doa based composition approach
def doa_composition(request, n, le):
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    req_id = 'doa_' + str(len(metrics) + 1)
    print('Request DOA: ' + req_id + ' ::: ' + request['name'] )
    topic = 'service.' + request['inputs'][0]['name']
    expected_output = request['outputs'][0]['name']
    message_dict = {'req_id': req_id, 'expected_output': expected_output, 'user_topic': 'user.response',
                    'desc': 'request from main!!!'}
    producer = Producer(credentials)
    measurement = {'id': req_id, 'name': request['name'], 'approach': 'doa', 'services': n, 'length': le,
                   'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = measurement
    producer.publish(topic, message_dict)


# conversation based composition approach
def conversation_composition(external_url, request, n, le):
    req_id = 'conversation_' + str(len(metrics) + 1)
    print('Request Conversation: ' + req_id + ' ::: ' + request['name'] )
    measurement = {'id': req_id, 'name': request['name'], 'approach': 'conversation', 'services': n, 'length': le,
                   'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = measurement
    plan = conversations.create_plan(request)
    tasks = plan['tasks']
    index = 1
    task = tasks['task_1']
    parameters = {'inputs': task['inputs']}
    while index <= len(tasks):
        task = tasks['task_' + str(index)]
        service = task['services'][0]
        print('requesting service: ' + service['path'])
        req = client.make_request(external_url, service['path'], parameters)
        parameters['inputs'] = req['outputs']
        index = index + 1
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    results.append(metrics[req_id])
    save(results_file, results, 'utf-8')


# planning based composition approach
def planning_composition(external_url, request, n, le):
    req_id = 'planning_' + str(len(metrics) + 1)
    print('Request Planning: ' + req_id + ' ::: ' + request['name'] )
    measurement = {'id': req_id, 'name': request['name'], 'approach': 'planning', 'services': n, 'length': le,
                   'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'total_time': 0}
    metrics[req_id] = measurement
    plan = backward_planning.create_plan(request)
    services = plan['services']
    index = len(services)
    parameters = {'inputs': request['inputs']}
    while index >= 1:
        service = services[index]
        print('requesting service: ' + service['path'])
        req = client.make_request(external_url, service['path'], parameters)
        parameters['inputs'] = req['outputs']
        index = index - 1
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    results.append(metrics[req_id])
    save(results_file, results, 'utf-8')


# main program that runs experiments
def main(parameters_file):

    # reading parameters file
    print('0. Reading experiment parameters...')
    file = open(parameters_file)
    parameters = json.load(file)
    experiment = parameters['experiment']
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
    create_dataset(experiment, dataset_path, services_number, requests_number, max_length)

    # deploying AWS resources
    print('2. Deploying resources...')
    external_url, rabbitmq_url = deploy_to_aws.deploy_resources('templates/doa-resources-template.yml',
                                                                './rabbit-mq.yaml')
    print('Load Balancer URL: ' + external_url)
    print('RabbitMQ Endpoint URL: ' + rabbitmq_url)
    print('3. Deploying services...')
    print('- Deploying asynchronous services')
    services_async = get_services('async', services_number, 1)
    deploy_to_aws.deploy_services('templates/doa-service-template.yml', services_async)
    rabbit_doa_consumer()
    print('- Deploying synchronous services')
    services_sync = get_services('sync', services_number, len(services_async) + 1)
    deploy_to_aws.deploy_services('templates/doa-service-template.yml', services_sync)
    data_access.remove_services()
    data_access.insert_services(services_sync)
    print('4. Executing experiments...')
    for length in lengths:
        i = 1
        while i <= experiment_requests:
            requests = get_requests(dataset_path, services_number, length)
            if 'doa' in approaches:
                #time.sleep(5)
                doa_composition(requests['goal'], services_number, length)
            if 'planning' in approaches:
                #time.sleep(5)
                planning_composition(external_url, requests['goal'], services_number, length)
            if 'conversation' in approaches:
                #time.sleep(5)
                conversation_composition(external_url, requests['conversation'], services_number, length)
            i = i + 1
    # removing services from AWS
    print('5. Removing services...')
    deploy_to_aws.remove_services(services_sync)
    deploy_to_aws.remove_services(services_async)
    data_access.remove_services()
    # removing AWS resources
    time.sleep(600)
    print('6. Removing resources...')
    deploy_to_aws.remove_resources()
    print(" *** Experiments finished *** ")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Please provide the experiments parameters file path in the correct format...')
