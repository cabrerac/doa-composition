from registry import data_access


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
