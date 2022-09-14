from registry import data_access


def create_plan(request):
    tasks = request['tasks']
    index = 1
    while index <= len(tasks):
        task = tasks['task_' + str(index)]
        query = {'outputs': task['outputs'], 'inputs': task['inputs']}
        services = data_access.get_services(query)
        task['services'] = services
        tasks['task_' + str(index)] = task
        index = index + 1
    request['tasks'] = tasks
    return request
