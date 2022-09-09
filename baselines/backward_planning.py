from registry import data_access


def create_plan(request):
    plan = {'id': request['id']}
    outputs = request['outputs']
    inputs = request['inputs']
    found = False
    services = {}
    while not found:
        query = {'outputs': outputs}
        service = data_access.get_services(query)
        services[len(services)+1] = service
        if inputs == service['inputs']:
            found = True
        else:
            outputs = service['outputs']
    return plan
