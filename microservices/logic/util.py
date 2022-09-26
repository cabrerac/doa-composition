from cfn_tools import load_yaml
import pika
import json


# reads credentials
def read_rabbit_credentials(file):
    with open(file, 'r') as stream:
        credentials = load_yaml(stream)
        return credentials


# publishes message on rabbitMQ
def publish_message(host, msg, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=msg,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ))
    connection.close()


# reads service description
def read_service_description(file):
    f = open(file)
    description = json.load(f)
    return description


# compares two lists of parameters
def compare(pars_1, pars_2):
    if len(pars_1) == len(pars_2):
        names_pars = []
        for par in pars_2:
            names_pars.append(par['name'])
        for par in pars_1:
            if par['name'] not in pars_2:
                return False
    else:
        return False
    return True


# compares if service outputs are in the expected outputs list
def compare_outputs(expected_outputs, service_outputs):
    for service_output in service_outputs:
        for expected_output in expected_outputs:
            if service_output['name'] == expected_output['name']:
                return True
    return False
