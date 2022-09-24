import json
import random
import os
from pathlib import Path
import networkx as nx
import shutil
from itertools import combinations


# creates experiment dataset
def create_dataset(path, experiment, deployable_services, requests_number, lengths):
    g = nx.barabasi_albert_graph(deployable_services, 2)
    dag = nx.DiGraph([(u, v, {'weight': random.randint(-10, 10)}) for (u, v) in g.edges() if u < v])
    if os.path.exists(path + experiment + '/'):
        shutil.rmtree(path + experiment + '/')
    print('- Creating services and requests for experiment ' + experiment + '...')
    create_services_descriptions(experiment, dag)
    print('- Creating services implementations for experiment ' + experiment + '...')
    create_services_implementations(experiment, dag)
    print('- Creating services requests for experiment ' + experiment + '...')
    create_services_requests(requests_number, lengths, dag, experiment, path, deployable_services)
    return list(dag.nodes)


# creates n services
def create_services_descriptions(experiment, dag):
    # creating dag services
    Path('./datasets/descriptions/' + experiment + '/services').mkdir(parents=True, exist_ok=True)
    Path('./datasets/descriptions/' + experiment + '/requests').mkdir(parents=True, exist_ok=True)
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
        with open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json','w') as f:
            json.dump(service_template, f, indent=2)
        services = services + 1


# creates services implementation for m services
def create_services_implementations(experiment, dag):
    for node in dag.nodes:
        t = random.random()
        t = t / 100
        t = round(t, 4)
        fin = open('./datasets/templates/service_template_sync.txt', 'rt')
        fout = open('./microservices/service_' + str(node) + '_sync.py', 'wt')
        file = open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            fout.write(line.replace('<service>', service_name).replace('<time>', str(t)))
        fin.close()
        fout.close()

        fin = open('./datasets/templates/service_template_async.txt', 'rt')
        fout = open('./microservices/service_' + str(node) + '_async.py', 'wt')
        file = open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            fout.write(line.replace('<service>', service_name).replace('<time>', str(t)))
        fin.close()
        fout.close()

        fin = open('./datasets/templates/docker-template-sync', 'rt')
        fout = open('./dockers/service-' + str(node) + '-sync', 'wt')
        file = open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            fout.write(line.replace('<service>', service_name).replace('<experiment>', experiment))
        fin.close()
        fout.close()

        fin = open('./datasets/templates/docker-template-async', 'rt')
        fout = open('./dockers/service-' + str(node) + '-async', 'wt')
        file = open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            fout.write(line.replace('<service>', service_name).replace('<experiment>', experiment))
        fin.close()
        fout.close()


# creates r requests for lengths based on a dag for a given experiment 
def create_services_requests(r, lengths, dag, experiment, path, deployable_services):
    Path('./datasets/descriptions/' + experiment + '/requests/goal').mkdir(parents=True, exist_ok=True)
    Path('./datasets/descriptions/' + experiment + '/requests/conversation').mkdir(parents=True, exist_ok=True)
    for length in lengths:
        Path('./datasets/descriptions/' + experiment + '/requests/goal/' + str(length) + '/').mkdir(parents=True, exist_ok=True)
        Path('./datasets/descriptions/' + experiment + '/requests/conversation/' + str(length) + '/').mkdir(parents=True, exist_ok=True)
        requests = []
        print('-- Creating requests for length ' + str(length) + '...') 
        for nodes in combinations(dag.nodes, length):
            dag_sub = dag.subgraph(nodes)
            if nx.is_weakly_connected(dag_sub):
                add = True
                for node in dag_sub.nodes:
                    predecessors = dag.predecessors(node)
                    predecessors = list(dict.fromkeys(predecessors))
                    for predecessor in predecessors:
                        if predecessor not in dag_sub.nodes:
                            add = False
                            break
                    if not add:
                        break
                if add:
                    requests.append(dag_sub)
            if len(requests) >= r:
                break
        if len(requests) == r:
            req = 0
            for request in requests:
                _create_conversation_request(experiment, length, req, request)
                _create_goal_request(experiment, length, req, request)
                req = req + 1
        else:
            print('Not enought requests in graph...')
            print('Recreating dataset...')
            create_dataset(path, experiment, deployable_services, r, lengths)


# creates request for goal-driven approaches (i.e., planning and doa)
def _create_goal_request(experiment, length, req, dag):
    request_file = './datasets/descriptions/' + experiment + '/requests/goal/' + str(length) + '/request_' + str(req) + '.json'
    firsts = []
    lasts = []
    for node in dag:
        predecessors = dag.predecessors(node)
        predecessors = list(dict.fromkeys(predecessors))
        if len(predecessors) == 0:
            firsts.append(node)
        successors = dag.successors(node)
        successors = list(dict.fromkeys(successors))
        if len(successors) == 0:
            lasts.append(node)
    inputs = []
    for node in firsts:
        file = open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json')
        service = json.load(file)
        for inp in service['inputs']:
            if inp not in inputs:
                inp['value'] = 'User input for request ' + str(req)
                inputs.append(inp)
    outputs = []
    for node in lasts:
        file = open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json')
        service = json.load(file)
        for output in service['outputs']:
            if output not in outputs:
                outputs.append(output)
    file = open('./datasets/templates/goal_request_template.json')
    goal_template = json.load(file)
    goal_template['inputs'] = inputs
    goal_template['outputs'] = outputs
    goal_template['name'] = 'request_' + str(req)
    if not os.path.exists(request_file):
        with open(request_file, 'w') as f:
            json.dump(goal_template, f, indent=2)


# creates request for conversation-based approach
def _create_conversation_request(experiment, length, req, dag):
    request_file = './datasets/descriptions/' + experiment + '/requests/conversation/' + str(length) + '/request_' + str(req) + '.json'
    tasks = {}
    inputs = {}
    for node in dag:
        file = open('./datasets/descriptions/' + experiment + '/services/service_' + str(node) + '.json')
        predecessors = dag.predecessors(node)
        predecessors = list(dict.fromkeys(predecessors))
        successors = dag.successors(node)
        successors = list(dict.fromkeys(successors))
        service = json.load(file)
        task = {'task': str(node), 'outputs': service['outputs'], 'inputs': service['inputs'], 'predecessors': predecessors,
                'successors': successors}
        tasks['task_' + str(node)] = task
        if len(predecessors) == 0:
            if node not in inputs.keys():
                inps = []
                for inp in service['inputs']:
                    inp['value'] = 'User input for request ' + str(req)
                    inps.append(inp)
                inputs[int(node)] = inps
    file = open('./datasets/templates/conversation_request_template.json')
    conversation_template = json.load(file)
    conversation_template['tasks'] = tasks
    conversation_template['name'] = 'request_' + str(req)
    conversation_template['inputs'] = inputs
    if not os.path.exists(request_file):
        with open(request_file, 'w') as f:
            json.dump(conversation_template, f, indent=2)


# defines services to deploy in the AWS infrastructure
def get_services(service_type, experiment, created_services, priority):
    services = []
    for node in created_services:
        file = open('./datasets/descriptions/' + experiment + '/services/service_'+str(node)+'.json')
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
    return services


# defines services to register in db
def get_services_to_register(service_type, experiment, services_number, created_services, priority):
    services = []
    for node in created_services:
        file = open('./datasets/descriptions/' + experiment + '/services/service_'+str(node)+'.json')
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
    while len(services) < services_number:
        file = open('./datasets/templates/service_template.json')
        service_template = json.load(file)
        service_template['inputs'][0]['name'] = '_INPUT_SERVICE_DUMMY_' + str(len(services))
        service_template['outputs'][0]['name'] = '_OUTPUT_SERVICE_DUMMY_' + str(len(services))
        service_template['name'] = 'dummy_service_' + str(len(services))
        service_template['description'] = 'This is the dummy service ' + str(len(services))
        services.append(service_template)
    return services


# gets service requests
def get_requests(path, experiment, experiment_requests, length):
    requests = []
    path = path + experiment + '/requests/goal/' + str(length) + '/'
    while len(requests) < experiment_requests:
        request_file = random.choice(os.listdir(path))
        if request_file not in requests:
            requests.append(request_file)
    return requests


# gets request
def get_request(path, experiment, approach, length, file_name):
    path = path + experiment + '/requests/' + approach + '/' + str(length) + '/' + file_name
    request = json.load(open(path))
    return request
