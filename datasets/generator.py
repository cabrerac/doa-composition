import json
import random
import os


# creates n services and r requests for lengths from 1 to le
def create_services_requests(n, r, le):
    # creating n services
    file = open('./datasets/templates/service_template.json')
    service_template = json.load(file)
    service = 1
    while service <= n:
        output = service
        inp = service - 1
        if service == 1:
            inp = n
        service_template['outputs'][0]['name'] = '_OUTPUT_SERVICE_' + str(output)
        service_template['inputs'][0]['name'] = '_OUTPUT_SERVICE_' + str(inp)
        service_template['name'] = 'service_' + str(service)
        service_template['description'] = 'This is the service ' + str(service)
        with open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(service) + '.json', 'w') as f:
            json.dump(service_template, f, indent=2)
        service = service + 1

    # creating r requests of lengths from 1 to le for goal and conversations approaches
    length = 1
    while length <= le:
        request = 1
        while request <= r:
            first = random.randint(1, n)
            last = first + length - 1
            if last > n:
                last = last - n
            output = './datasets/descriptions/' + str(n) + '-services/requests/goal/' + str(length) + '/request_' + \
                     str(first) + '_' + str(last) + '.json'
            if not os.exists(output):
                create_goal_request(output, n, first, last)
                output = output.replace('goal', 'conversation')
                create_conversation_request(output, n, first, last)
                request = request + 1
        length = length + 1

    # creating r requests of lengths from 1 to le for conversation approaches
    length = 1
    while length <= le:
        request = 1
        while request <= r:
            first = random.randint(1, n)
            last = first + length - 1
            if last > n:
                last = last - n

                request = request + 1
        length = length + 1


# creates request for goal-driven approaches (i.e., planning and doa)
def create_goal_request(output, n, first, last):
    file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(first) + '.json')
    first_service = json.load(file)
    file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(last) + '.json')
    last_service = json.load(file)
    file = open('./datasets/templates/goal_request_template.json')
    goal_template = json.load(file)
    goal_template['outputs'] = last_service['outputs']
    goal_template['inputs'] = first_service['inputs']
    if not os.exists(output):
        with open(output, 'w') as f:
            json.dump(goal_template, f, indent=2)


# creates request for conversation-based approach
def create_conversation_request(output, n, first, last):
    current = first
    tasks = []
    t = 1
    if current == last:
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(current) + '.json')
        current_service = json.load(file)
        task = {'task': t, 'outputs': current_service['outputs'], 'inputs': current_service['inputs']}
        tasks.append(task)
    else:
        while current != last:
            file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(current) + '.json')
            current_service = json.load(file)
            task = {'task': t, 'outputs': current_service['outputs'], 'inputs': current_service['inputs']}
            tasks.append(task)
            t = t + 1
            current = current + 1
            if current > n:
                current = current - n
    file = open('./datasets/descriptions/templates/conversation_request_template.json')
    conversation_template = json.load(file)
    conversation_template['tasks'] = tasks
    if not os.exists(output):
        with open(output, 'w') as f:
            json.dump(conversation_template, f, indent=2)


# creates services implementation
def create_services(n):
    s = 1
    while s <= n:
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
            fout.write(line.replace('<service>', service_name))
        # close input and output files
        fin.close()
        fout.close()

        # Writing sync dockerfiles
        fin = open('./datasets/templates/docker-template-async', 'rt')
        fout = open('./dockers/service-' + str(s) + '-async', 'wt')
        # for each line in the input file
        file = open('./datasets/descriptions/' + str(n) + '-services/services/service_' + str(s) + '.json')
        service = json.load(file)
        service_name = service['name']
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace('<service>', service_name))
        # close input and output files
        fin.close()
        fout.close()
        s = s + 1
