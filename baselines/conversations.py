from registry import data_access


def create_plan(request):
    tasks = request['tasks']
    for task in tasks:
        query = {'outputs': task['outputs'], 'inputs': task['inputs']}
        services = data_access.get_services(query)
        task['services'] = services
    request['tasks'] = tasks
    return request
