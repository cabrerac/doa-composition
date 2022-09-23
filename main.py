import time
import json
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
from results import plotting


# experimental setup variables
metrics = {}
results = []
rabbit_credentials_file = 'rabbit-mq.yaml'
dataset_path = './datasets/descriptions/'
results_file = ''


# writes results file
def save(file_name, res, fmt):
    df = pd.DataFrame.from_dict(res)
    df = df.drop(columns=['request_time', 'response_time'])
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', newline='', encoding=fmt) as f:
        df.to_csv(f, encoding=fmt, index=False, header=f.tell() == 0)


# doa based rabbit consumer
def rabbit_doa_consumer():
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    consumer_thread = Consumer(credentials, 'user.response', callback)
    consumer_thread.start()
    time.sleep(10)


# callback function for the doa based composition
def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    print('Response DOA request: ' + req_id)
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['total_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    metrics[req_id]['execution_time'] = metrics[req_id]['total_time']
    metrics[req_id]['messages_size'] = message['messages_size']
    results.append(metrics[req_id])
    save(results_file, results, 'utf-8')


# doa based composition approach
def doa_composition(request, n, le):
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    req_id = 'doa_' + str(len(metrics) + 1)
    print('Request DOA: ' + req_id + ' ::: ' + request['name'] )
    topic = 'service.' + request['inputs'][0]['name']
    expected_output = request['outputs'][0]['name']
    message_dict = {'req_id': req_id, 'expected_output': expected_output, 'user_topic': 'user.response',
                    'desc': 'request from main!!!'}
    message_dict['messages_size'] = sys.getsizeof(str(message_dict))
    producer = Producer(credentials)
    measurement = {'id': req_id, 'name': request['name'], 'approach': 'doa', 'services': n, 'length': le,
                   'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'planning_time': 0,
                   'execution_time': 0, 'total_time': 0, 'messages_size': 0, 'input_size': sys.getsizeof(str(request))}
    producer.publish(topic, message_dict)
    metrics[req_id] = measurement
    

# conversation based composition approach
def conversation_composition(external_url, request, n, le):
    req_id = 'conversation_' + str(len(metrics) + 1)
    print('Request Conversation: ' + req_id + ' ::: ' + request['name'] )
    measurement = {'id': req_id, 'name': request['name'], 'approach': 'conversation', 'services': n, 'length': le,
                   'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'planning_time': 0,
                   'execution_time': 0, 'total_time': 0, 'messages_size': 0, 'input_size': sys.getsizeof(str(request))}
    metrics[req_id] = measurement
    request, plan = conversations.create_plan(request)
    measurement['planning_time'] = int(round(time.time() * 1000)) - measurement['request_time']
    measurement['request_time'] = int(round(time.time() * 1000))
    responses = conversations.execute_plan(request, plan, external_url)
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['execution_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    metrics[req_id]['total_time'] = metrics[req_id]['planning_time'] + metrics[req_id]['execution_time']
    for response in responses:
        request_size = sys.getsizeof(str(response.request.method)) + sys.getsizeof(str(response.request.url)) \
                       + sys.getsizeof(str(response.request.headers)) + sys.getsizeof(str(response.request.body))
        metrics[req_id]['messages_size'] = metrics[req_id]['messages_size'] + request_size
    results.append(metrics[req_id])
    save(results_file, results, 'utf-8')


# planning based composition approach
def planning_composition(external_url, request, n, le):
    req_id = 'planning_' + str(len(metrics) + 1)
    print('Request Planning: ' + req_id + ' ::: ' + request['name'] )
    measurement = {'id': req_id, 'name': request['name'], 'approach': 'planning', 'services': n, 'length': le,
                   'request_time': int(round(time.time() * 1000)), 'response_time': 0, 'planning_time': 0,
                   'execution_time': 0, 'total_time': 0, 'messages_size': 0, 'input_size': sys.getsizeof(str(request))}
    metrics[req_id] = measurement
    services, plan = backward_planning.create_plan(request)
    measurement['planning_time'] = int(round(time.time() * 1000)) - measurement['request_time']
    measurement['request_time'] = int(round(time.time() * 1000))
    responses = backward_planning.execute_plan(request, services, plan, external_url)
    metrics[req_id]['response_time'] = int(round(time.time() * 1000))
    metrics[req_id]['execution_time'] = metrics[req_id]['response_time'] - metrics[req_id]['request_time']
    metrics[req_id]['total_time'] = metrics[req_id]['planning_time'] + metrics[req_id]['execution_time']
    for response in responses:
        request_size = sys.getsizeof(str(response.request.method)) + sys.getsizeof(str(response.request.url)) \
                       + sys.getsizeof(str(response.request.headers)) + sys.getsizeof(str(response.request.body))
        metrics[req_id]['messages_size'] = metrics[req_id]['messages_size'] + request_size
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
    lengths = parameters['lengths']
    services = parameters['services']
    requests_number = parameters['requests_number']
    experiment_requests = parameters['experiment_requests']
    deployable_services = 40
    global results_file
    results_file = parameters['results_file']

    # deploying AWS resources
    print('1. Deploying resources...')
    #external_url, rabbitmq_url = deploy_to_aws.deploy_resources('templates/doa-resources-template.yml', './rabbit-mq.yaml')
    #print('Load Balancer URL: ' + external_url)
    #print('RabbitMQ Endpoint URL: ' + rabbitmq_url)
    external_url = ''

    print('2. Creating experiment datasets...')
    created_services = generator.create_dataset(dataset_path, experiment, deployable_services, requests_number, lengths)
    print('3. Deploying services in AWS...')
    print('- Deploying asynchronous services')
    services_async = generator.get_services('async', experiment, created_services, 1)
    #deploy_to_aws.deploy_services('templates/doa-service-template.yml', services_async)
    #rabbit_doa_consumer()
    print('- Deploying synchronous services')
    services_sync = generator.get_services('sync', experiment, created_services, len(services_async) + 1)
    #deploy_to_aws.deploy_services('templates/doa-service-template.yml', services_sync)
    data_access.remove_services()

    # Running experiments
    print('4. Running experiments...')
    for services_number in services:
        print('- Registering services: ' + str(services_number))
        registry_services = generator.get_services_to_register('sync', experiment, services_number, created_services, len(services_async) + 1)
        data_access.insert_services(registry_services)
        print('- Defining requests for experiment with ' + str(services_number) + ' services...')
        all_requests = {}
        for length in lengths:
            all_requests[length] = generator.get_requests(dataset_path, experiment, experiment_requests, length)
        print('- Requesting services for experiment with ' + str(services_number) + ' services...')
        for approach in approaches:
            for length in lengths:
                requests = all_requests[length]
                i = 0
                while i < experiment_requests:
                    request_file = requests[i]
                    if approach == 'doa':
                        request = generator.get_request(dataset_path, experiment, 'goal', length, request_file)
                        #doa_composition(request, services_number, length)
                    if approach == 'planning':
                        request = generator.get_request(dataset_path, experiment, 'goal', length, request_file)
                        planning_composition(external_url, request, services_number, length)
                        time.sleep(2)
                    if approach == 'conversation':
                        request = generator.get_request(dataset_path, experiment, 'conversation', length, request_file)
                        #conversation_composition(external_url, request, services_number, length)
                    i = i + 1
        data_access.remove_services()
    # removing services from AWS
    print('7. Removing services...')
    #deploy_to_aws.remove_services(services_sync)
    #deploy_to_aws.remove_services(services_async)
    # plotting results
    print('8. Plotting results...')
    #plotting.plot_results(parameters)
    print('Waiting before removing resources...')
    #time.sleep(600)
    # removing AWS resources
    print('9. Removing resources...')
    #deploy_to_aws.remove_resources()
    print(" *** Experiments finished *** ")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Please provide the experiments parameters file path in the correct format...')

