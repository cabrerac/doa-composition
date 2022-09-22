from registry import data_access
import networkx as nx
import random

from clients import client


def create_plan(request):
    outputs = request['outputs']
    inputs = request['inputs']
    g = nx.Graph()
    services, g = _backward_planning(inputs, outputs, g, [], -2)
    dag = nx.DiGraph([(u, v, {'weight': random.randint(-10, 10)}) for (u, v) in g.edges() if u < v])
    sources = []
    for node in dag.nodes:
        predecessors = dag.predecessors(node)
        predecessors = list(dict.fromkeys(predecessors))
        if len(predecessors) == 0:
            if node not in sources:
                sources.append(node)
    plan = dict(enumerate(nx.bfs_layers(dag, sources)))
    return services, plan


def _backward_planning(inputs, outputs, graph, services, node):
    if inputs != outputs:
        for output in outputs:
            query = {'outputs.name': output['name']}
            services = data_access.get_services(query)
            for service in service:
                graph_temp = graph.copy(as_view=False)
                graph_temp.add_edge(service['name'], node)
                outputs_temp = service['inputs']
                for output_temp in outputs_temp:
                    if output_temp != output:
                        outputs_temp.append(output)
                services_temp = services
                services_temp.append(service)
                services, graph = _backward_planning(inputs, outputs_temp, services_temp, service['name'])
    else:
        return services, graph
    return services, graph


def execute_plan(request, plan, external_url):
    print('- executing plan...')
    services = plan['services']
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


