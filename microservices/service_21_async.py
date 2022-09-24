from flask import Flask, make_response
import logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer
import time
import json
import sys
from logic import util


rabbit_credentials_file = 'rabbit-mq.yaml'
description = util.read_service_description('./description/service_21.json')
requests = {}


# callback to process asynchronous messages
def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    inputs = []
    if req_id in requests:
        inputs = requests[req_id]
    for output in message['outputs']:
        inputs.append(output)
    if _compare(inputs, description['inputs'])
        user_topic = message['user_topic']
        expected_output = message['expected_output']
        messages_size = message['messages_size']
        ms = 0.0073
        time.sleep(ms)
        outputs = description['outputs']
        for output in outputs:
            output['value'] = 'Output value from ' + description['name']
        message_dict = {
            'req_id': req_id, 'user_topic': user_topic, 'expected_output': expected_output, 'desc': 'message from ' + description['name'] + '_async', 'next_topic': 'service.' + outputs[0]['name'],
            'outputs': outputs
        }
        messages_size = messages_size + sys.getsizeof(str(message_dict))
        message_dict['messages_size'] = messages_size
        next_topic = message_dict['next_topic']
        if expected_output == outputs[0]['name']:
            next_topic = user_topic
        credentials = util.read_rabbit_credentials(rabbit_credentials_file)
        producer = Producer(credentials)
        producer.publish(next_topic, message_dict)
        if req_id in requests:
            del requests[req_id]
    else:
        requests[req_id] = inputs


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


# creates a messages listener per each service input
credentials = util.read_rabbit_credentials(rabbit_credentials_file)
inputs = description['inputs']
for inp in inputs:
    consumer_thread = Consumer(credentials, 'service.' + inp['name'], callback)
    consumer_thread.start()


# flask interface
app = Flask('__name__')


# single endpoint to pass AWS health checks
@app.route('/doa_composition/service_21_async', methods=['GET', 'POST'])
def service_21_async():
    try:
        return make_response({'res': ""})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
