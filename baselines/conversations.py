from registry import data_access
import networkx as nx
import random

from clients import client


# creates plan for the request
def create_plan(request):
    print('- creating plan...')
    tasks = request['tasks']
    g = nx.Graph()
    for key, task in tasks.items():
        outputs_names = []
        for output in task['outputs']:
            if output['name'] not in outputs_names:
                outputs_names.append(output['name'])
        inputs_names = []
        for input in task['inputs']:
            if input['name'] not in inputs_names:
                inputs_names.append(input['name'])
        query = {'outputs.name': {'$in': outputs_names}, 'inputs.name': {'$in': inputs_names}}
        services = data_access.get_services(query)
        task['services'] = services
        tasks[key] = task
        predecessors = task['predecessors']
        successors = task['successors']
        for predecessor in predecessors:
            if (int(predecessor), int(task['task'])) not in g.edges:
                g.add_edge(int(predecessor), int(task['task']))
        for successor in successors:
            if (int(task['task']), int(successor)) not in g.edges:
                g.add_edge(int(task['task']), int(successor))
    request['tasks']
    dag = nx.DiGraph([(u, v, {'weight': random.randint(-10, 10)}) for (u, v) in g.edges() if u < v])
    sources = []
    for node in dag.nodes:
        predecessors = dag.predecessors(node)
        predecessors = list(dict.fromkeys(predecessors))
        if len(predecessors) == 0:
            if node not in sources:
                sources.append(node)
    plan = dict(enumerate(nx.bfs_layers(dag, sources)))
    return request, plan


# executes a composition plan
def execute_plan(request, plan, external_url):
    print('- executing plan...')
    index = 0
    outputs = {}
    executed = []
    responses = []
    while index < len(plan):
        values = plan[index]
        for value in values:
            task = request['tasks']['task_' + str(value)]
            predecessors = task['predecessors']
            ready = True
            for predecessor in predecessors:
                if predecessor not in executed:
                    if (index + 1) in plan:
                        plan[index+1].append(value)
                    else:
                        plan[index+1] = [value]
                    ready = False
                    break
            if ready:
                service = task['services'][0]
                print('requesting service: ' + service['path'])
                parameters = {}
                if index == 0:
                    parameters = {'inputs': request['inputs'][str(value)]}
                else:
                    inputs = []
                    for predecessor in predecessors:
                        if predecessor in outputs:
                            for output in outputs[predecessor]:
                                inputs.append(output)
                    parameters = {'inputs': inputs}
                response = client.make_request(external_url, service['path'], parameters)
                print(response.text)
                responses.append(response)
                outputs[value] = response.json()['outputs']
                executed.append(value)
        index = index + 1
    return responses
