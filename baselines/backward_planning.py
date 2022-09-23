from registry import data_access
import networkx as nx
import random
import time

from clients import client


def create_plan(request):
    outputs = request['outputs']
    inputs = []
    for inp in request['inputs']:
        inputs.append({'name': inp['name'], 'type': inp['type']})
    plan = {'graph': nx.Graph(), 'inputs': inputs, 'outputs': outputs, 'services': [], 'finished': False}
    plans = [plan]
    plans = _backward_planning(plans)
    """dag = nx.DiGraph([(u, v, {'weight': random.randint(-10, 10)}) for (u, v) in g.edges() if u < v])
    sources = []
    for node in dag.nodes:
        predecessors = dag.predecessors(node)
        predecessors = list(dict.fromkeys(predecessors))
        if len(predecessors) == 0:
            if node not in sources:
                sources.append(node)
    plan = dict(enumerate(nx.bfs_layers(dag, sources)))
    return services, plan"""


def _backward_planning(plans):
    var = input("Please enter something: ")
    if _finished(plans):
        return plans
    else:
        temp_plans = []
        for plan in plans:
            temp_plan = {'inputs': plan['inputs'], 'graph': plan['graph'].copy(as_view=False), 'services': []}
            for ser in plan['services']:
                if ser not in temp_plan['services']:
                    temp_plan['services'].append(ser)
            print('*** NODES... ***')
            print(plan['graph'].nodes)
            print('*** EDGES... ***')
            print(plan['graph'].edges)
            print('*** INPUTS/OUTPUTS ***')
            inputs = plan['inputs']
            print(inputs)
            outputs = plan['outputs']
            print(outputs)
            for output in outputs:
                query = {'outputs.name': output['name']}
                services = data_access.get_services(query)
                print('*** RETURNED SERVICES  ***')
                print(str(len(services)))
                if len(services) > 0:
                    service = services[0]
                    print('*** SERVICE... ***')
                    print(service['name'])
                    services_temp = []
                    for ser in temp_plan['services']:
                        services_temp.append(ser)
                    if service not in services_temp:
                        services_temp.append(service)
                    temp_plan['services'] = services_temp
                    new_node = int(service['name'].split('_')[1])
                    temp_plan['graph'].add_node(new_node)
                    nodes = []
                    for ser in temp_plan['services']:
                        for service_output in service['outputs']:
                            if service_output in ser['inputs']:
                                if ser['name'].split('_')[1] not in nodes:
                                    nodes.append(ser['name'].split('_')[1])
                    for node in nodes:
                        print('*** EDGE... ***')
                        print(str(int(new_node)) + '-' + str(node))
                        if (int(new_node), int(node)) not in temp_plan['graph'].edges:
                            temp_plan['graph'].add_edge(int(new_node), int(node))
                    temp_outputs = []
                    if 'outputs' in temp_plan:
                        for temp_output in temp_plan['outputs']:
                            temp_outputs.append(temp_output)
                    for temp_output in service['inputs']:
                        if temp_output not in temp_outputs:
                            temp_outputs.append(temp_output)
                    temp_plan['outputs'] = temp_outputs
                    if _compare(temp_plan['inputs'], temp_plan['outputs']):
                        temp_plan['finished'] = True
                    else:
                        temp_plan['finished'] = False 
            temp_plans.append(temp_plan)
        plans = _backward_planning(temp_plans)


def _finished(plans):
    for plan in plans:
        if plan['finished'] == True:
            return True
    return False


def _compare(inputs, outputs):
    if len(inputs) == len(outputs):
       index = 0
       while index < len(inputs):
           if inputs[index]['name'] != outputs[index]['name']:
               return False
           index = index + 1
    else:
        return False
    return True


def execute_plan(request, services, plan, external_url):
    print('- executing plan...')
    index = len(services)
    parameters = {'inputs': request['inputs']}
    responses = []
    while index >= 1:
        service = services[index]
        print('requesting service: ' + service['path'])
        response = client.make_request(external_url, service['path'], parameters)
        parameters['inputs'] = response.json()['outputs']
        responses.append(response)
        index = index - 1


