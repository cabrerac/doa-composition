import json
import random
import os


# creates n services
def create_services_descriptions(n, m):
    # creating n services
    file = open('./datasets/templates/service_template.json')
    service_template = json.load(file)
    service = 1
    os.mkdir('./datasets/descriptions/')
    os.mkdir('./datasets/descriptions/' + str(n) + '-services/')
    os.mkdir('./datasets/descriptions/' + str(n) + '-services/services')
    os.mkdir('./datasets/descriptions/' + str(n) + '-services/requests')
    while service <= n:
        output = service
        inp = service - 1
        if service == 1:
            inp = m
        service_template['outputs'][0]['name'] = '_OUTPUT_SERVICE_' + str(output)
        service_template['inputs'][0]['name'] = '_OUTPUT_SERVICE_' + str(inp)
        service_template['name'] = 'service_' + str(service)
        service_template['description'] = 'This is the service ' + str(service)
        with open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(service) + '.json', 'w') as f:
            json.dump(service_template, f, indent=2)
        service = service + 1


# creates r requests for lengths based on m services for the experiment with n services
def create_services_requests(r, lengths, m, n):
    # creating r requests for lengths for goal and conversations approaches
    os.mkdir('./datasets/descriptions/' + str(n) + '-services/requests/goal/')
    os.mkdir('./datasets/descriptions/' + str(n) + '-services/requests/conversation/')
    for length in lengths:
        os.mkdir('./datasets/descriptions/' + str(n) + '-services/requests/goal/' + str(length) + '/')
        os.mkdir('./datasets/descriptions/' + str(n) + '-services/requests/conversation/' + str(length) + '/')
        request = 1
        while request <= r:
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
                request = request + 1


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


# creates services implementation for m services
def create_services_implementations(n, m):
    s = 1
    while s <= m:
        t = random.random()
        t = t / 100
        t = round(t, 4)
        # Writing sync services
        fin = open('./datasets/templates/service_template_sync.txt', 'rt')
        fout = open('./microservices/service_' + str(s) + '_sync.py', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(s) + '.json')
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
        fout = open('./microservices/service_' + str(s) + '_async.py', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(s) + '.json')
        service = json.load(file)
        service_name = service['name']
        service_output = service['outputs'][0]['name']
        service_input = service['inputs'][0]['name']
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace('<service>', service_name).replace('<time>', str(t)).
                       replace('<input_name>', service_input).replace('<output_name>', service_output))
        # close input and output files
        fin.close()
        fout.close()

        # Writing sync dockerfiles
        fin = open('./datasets/templates/docker-template-sync', 'rt')
        fout = open('./dockers/service-' + str(s) + '-sync', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(s) + '.json')
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
        fout = open('./dockers/service-' + str(s) + '-async', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(s) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace('<service>', service_name).replace('<experiment>', str(n)+'-services'))
        # close input and output files
        fin.close()
        fout.close()
        s = s + 1
