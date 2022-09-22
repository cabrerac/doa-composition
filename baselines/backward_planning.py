from registry import data_access

from clients import client


def create_plan(request):
    plan = {'name': request['name']}
    outputs = request['outputs']
    inputs = request['inputs']
    found = False
    services = {}
    while outputs != inputs:
        query = {'outputs': outputs}
        service = data_access.get_services(query)[0]
        services[len(services)+1] = service
        outputs = service['inputs']
        plan['services'] = services
    return plan


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


