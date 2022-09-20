import json
import random
import os
from pathlib import Path
import networkx as nx
import shutil
from itertools import combinations
import matplotlib.pyplot as plt


# creates experiment dataset
def create_dataset(path, services_number, deployable_services, requests_number, lengths):
    if os.path.exists(path + str(services_number) + '-services/'):
        shutil.rmtree(path + str(services_number) + '-services/')
    g = nx.gnp_random_graph(deployable_services, 0.1, directed=True)
    dag = nx.DiGraph([(u, v, {'weight': random.randint(-10, 10)}) for (u, v) in g.edges() if u < v])
    print('- Creating services and requests for experiment with ' + str(services_number) + ' services...')
    create_services_descriptions(services_number, dag)
    print('- Creating services implementations for experiment with ' + str(services_number) + ' services...')
    create_services_implementations(services_number, dag)
    print('- Creating services requests for experiment with ' + str(services_number) + ' services...')
    create_services_requests(requests_number, lengths, dag, services_number)


# creates n services
def create_services_descriptions(n, dag):
    # creating dag services
    Path('./datasets/descriptions/' + str(n) + '-services/services').mkdir(parents=True, exist_ok=True)
    Path('./datasets/descriptions/' + str(n) + '-services/requests').mkdir(parents=True, exist_ok=True)
    services = 0
    for node in dag.nodes:
        file = open('./datasets/templates/service_template.json')
        service_template = json.load(file)
        predecessors = dag.predecessors(node)
        predecessors = list(dict.fromkeys(predecessors))
        if len(predecessors) == 0:
            service_template['inputs'][0]['name'] = '_INPUT_SERVICE_' + str(node)
        else:
            inputs = []
            for predecessor in predecessors:
                inp = {'name': '_OUTPUT_SERVICE_' + str(predecessor),
                       'type': 'http://www.autoai.cam.ac.uk/dtypes.owl#numeric'}
                inputs.append(inp)
            service_template['inputs'] = inputs
        service_template['outputs'][0]['name'] = '_OUTPUT_SERVICE_' + str(node)
        service_template['name'] = 'service_' + str(node)
        service_template['description'] = 'This is the service ' + str(node)
        with open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(node) + '.json','w') as f:
            json.dump(service_template, f, indent=2)
        services = services + 1

    while services < n:
        file = open('./datasets/templates/service_template.json')
        service_template = json.load(file)
        service_template['inputs'][0]['name'] = '_INPUT_SERVICE_DUMMY_' + str(services)
        service_template['outputs'][0]['name'] = '_OUTPUT_SERVICE_DUMMY_' + str(services)
        service_template['name'] = 'service_' + str(services)
        service_template['description'] = 'This is the service ' + str(services)
        with open('./datasets/descriptions/' + str(n) + '-services/services/dummy-service' + str(services) + '.json', 'w') as f:
            json.dump(service_template, f, indent=2)
        services = services + 1


# creates services implementation for m services
def create_services_implementations(n, dag):
    for node in dag.nodes:
        t = random.random()
        t = t / 100
        t = round(t, 4)
        # Writing sync services
        fin = open('./datasets/templates/service_template_sync.txt', 'rt')
        fout = open('./microservices/service_' + str(node) + '_sync.py', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace('<service>', service_name).replace('<time>', str(t)))
        # close input and output files
        fin.close()
        fout.close()

        # Writing async services
        fin = open('./datasets/templates/service_template_async.txt', 'rt')
        fout = open('./microservices/service_' + str(node) + '_async.py', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace('<service>', service_name).replace('<time>', str(t)))
        # close input and output files
        fin.close()
        fout.close()

        # Writing sync dockerfiles
        fin = open('./datasets/templates/docker-template-sync', 'rt')
        fout = open('./dockers/service-' + str(node) + '-sync', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace('<service>', service_name).replace('<experiment>', str(n)+'-services'))
        # close input and output files
        fin.close()
        fout.close()

        # Writing async dockerfiles
        fin = open('./datasets/templates/docker-template-async', 'rt')
        fout = open('./dockers/service-' + str(node) + '-async', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace('<service>', service_name).replace('<experiment>', str(n)+'-services'))
        # close input and output files
        fin.close()
        fout.close()


# creates r requests for lengths based on a dag for the experiment with n services
def create_services_requests(r, lengths, dag, n):
    # creating r requests for lengths for goal and conversations approaches
    Path('./datasets/descriptions/' + str(n) + '-services/requests/goal').mkdir(parents=True, exist_ok=True)
    Path('./datasets/descriptions/' + str(n) + '-services/requests/conversation').mkdir(parents=True, exist_ok=True)
    for length in lengths:
        Path('./datasets/descriptions/' + str(n) + '-services/requests/goal/' + str(length) + '/').mkdir(parents=True, exist_ok=True)
        Path('./datasets/descriptions/' + str(n) + '-services/requests/conversation/' + str(length) + '/').mkdir(parents=True, exist_ok=True)
        requests = []
        i = 0
        for nodes in combinations(dag.nodes, length):
            dag_sub = dag.subgraph(nodes)
            if nx.is_weakly_connected(dag_sub):
                requests.append(dag_sub)
                nx.draw(dag_sub, with_labels=True)
                plt.show()
            if len(requests) >= r:
                break
            i = i = 1

        print('here')
        """request = 0
        while request < r:
            first = random.randint(1, m)
            last = first + length - 1
            if last > m:
                last = last - m
            output = './datasets/descriptions/' + str(n) + '-services/requests/goal/' + str(length) + '/request_' + \
                     str(first) + '_' + str(last) + '.json'
            name = 'request_' + str(first) + '_' + str(last)
            if not os.path.exists(output):
                _create_goal_request(name, output, n, first, last)
                output = output.replace('goal', 'conversation')
                _create_conversation_request(name, output, n, first, last)
                request = request + 1"""


# creates request for goal-driven approaches (i.e., planning and doa)
def _create_goal_request(name, output, n, first, last):
    file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(first) + '.json')
    first_service = json.load(file)
    file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(last) + '.json')
    last_service = json.load(file)
    file = open('./datasets/templates/goal_request_template.json')
    goal_template = json.load(file)
    goal_template['outputs'] = last_service['outputs']
    goal_template['inputs'] = first_service['inputs']
    goal_template['name'] = name
    if not os.path.exists(output):
        with open(output, 'w') as f:
            json.dump(goal_template, f, indent=2)


# creates request for conversation-based approach
def _create_conversation_request(name, output, n, first, last):
    current = first
    tasks = {}
    t = 1
    if current == last:
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(current) + '.json')
        current_service = json.load(file)
        task = {'task': t, 'outputs': current_service['outputs'], 'inputs': current_service['inputs']}
        tasks['task_' + str(t)] = task
    else:
        while current != last:
            file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(current) + '.json')
            current_service = json.load(file)
            task = {'task': t, 'outputs': current_service['outputs'], 'inputs': current_service['inputs']}
            tasks['task_' + str(t)] = task
            t = t + 1
            current = current + 1
            if current > n:
                current = current - n
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(current) + '.json')
        current_service = json.load(file)
        task = {'task': t, 'outputs': current_service['outputs'], 'inputs': current_service['inputs']}
        tasks['task_' + str(t)] = task
    file = open('./datasets/templates/conversation_request_template.json')
    conversation_template = json.load(file)
    conversation_template['tasks'] = tasks
    conversation_template['name'] = name
    if not os.path.exists(output):
        with open(output, 'w') as f:
            json.dump(conversation_template, f, indent=2)


# defines services to register and deploy in the AWS infrastructure
def get_services(service_type, services_number, deployable_services, priority):
    services = []
    i = 1
    while i <= deployable_services:
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


# gets service requests
def get_requests(path, services_number, experiment_requests, length):
    requests = []
    path = path + str(services_number) + '-services/requests/goal/' + str(length) + '/'
    while len(requests) < experiment_requests:
        request_file = random.choice(os.listdir(path))
        if request_file not in requests:
            requests.append(request_file)
    return requests


# gets request
def get_request(path, services_number, approach, length, file_name):
    path = path + str(services_number) + '-services/requests/' + approach + '/' + str(length) + '/' + file_name
    request = json.load(open(path))
    return request
