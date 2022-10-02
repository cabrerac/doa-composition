from registry import data_access
import networkx as nx
import random
import time

from clients import client


# creates plan for the request
def create_plan(request):
    print('creating plan...')
    outputs = request['outputs']
    inputs = []
    for inp in request['inputs']:
        inputs.append({'name': inp['name'], 'type': inp['type']})
    plan = {'graph': nx.DiGraph(), 'inputs': inputs, 'outputs': outputs, 'services': {}, 'finished': False}
    plans = [plan]
    plans = _backward_planning(plans)
    for plan in plans:
        if plan['finished']:
            services = plan['services']
            graph = plan['graph']
            dag = nx.DiGraph([(u, v, {'weight': random.randint(-10, 10)}) for (u, v) in graph.edges() if u < v])
            sources = []
            for node in dag.nodes:
                predecessors = dag.predecessors(node)
                predecessors = list(dict.fromkeys(predecessors))
                if len(predecessors) == 0:
                    if node not in sources:
                        sources.append(node)
            plan = dict(enumerate(nx.bfs_layers(dag, sources)))
            return services, graph, plan


# backward planning algorithm to discover composition of services by matching outputs and inputs
def _backward_planning(plans):
    if _finished(plans):
        return plans
    else:
        temp_plans = []
        for plan in plans:
            temp_plan = {'inputs': plan['inputs'], 'graph': plan['graph'].copy(as_view=False), 'services': {}}
            for key, ser in plan['services'].items():
                if key not in temp_plan['services']:
                    temp_plan['services'][key] = ser
            outputs = plan['outputs']
            for output in outputs:
                query = {'outputs.name': output['name']}
                services = data_access.get_services(query)
                if len(services) > 0:
                    service = services[0]
                    services_temp = {}
                    for key, ser in temp_plan['services'].items():
                        services_temp[key] = ser
                    if service['name'].split('_')[1] not in services_temp:
                        services_temp[int(service['name'].split('_')[1])] = service
                    temp_plan['services'] = services_temp
                    new_node = int(service['name'].split('_')[1])
                    temp_plan['graph'].add_node(new_node)
                    nodes = []
                    for key, ser in temp_plan['services'].items():
                        for service_output in service['outputs']:
                            if service_output in ser['inputs']:
                                if ser['name'].split('_')[1] not in nodes:
                                    nodes.append(ser['name'].split('_')[1])
                    for node in nodes:
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
        return plans


# validates when the backward algorithm should finish
def _finished(plans):
    for plan in plans:
        if plan['finished']:
            return True
    return False


# compares two lists of parameters
def _compare(pars_1, pars_2):
    if len(pars_1) == len(pars_2):
        index = 0
        while index < len(pars_1):
            if pars_1[index]['name'] != pars_2[index]['name']:
                return False
            index = index + 1
    else:
        return False
    return True


# executes a composition plan
def execute_plan(request, services, graph, plan, external_url):
    print('- executing plan...')
    index = 0
    outputs = {}
    executed = []
    responses = []
    while index < len(plan):
        values = plan[index]
        for value in values:
            predecessors = graph.predecessors(value)
            predecessors = list(dict.fromkeys(predecessors))
            ready = True
            for predecessor in predecessors:
                if predecessor not in executed:
                    if (index + 1) in plan:
                        plan[index + 1].append(value)
                    else:
                        plan[index + 1] = [value]
                    ready = False
                    break
            if ready:
                service = services[value]
                parameters = {}
                if index == 0:
                    parameters = {'inputs': request['inputs']}
                else:
                    inputs = []
                    for predecessor in predecessors:
                        print('predecessor: ' + str(predecessor))
                        print(str(outputs))
                        if predecessor in outputs:
                            for output in outputs[predecessor]:
                                inputs.append(output)
                    parameters = {'inputs': inputs}
                print('requesting service: ' + service['path'])
                response = client.make_request(external_url, service['path'], parameters)
                responses.append(response)
                outputs[value] = response.json()['outputs']
                executed.append(value)
        index = index + 1
    return responses
