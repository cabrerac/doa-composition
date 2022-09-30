from flask import Flask, make_response
import logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer
import time
import json
import sys
from logic import util


rabbit_credentials_file = 'rabbit-mq.yaml'
description = util.read_service_description('./description/service_36.json')
requests = {}


# callback to process asynchronous messages
def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    try:
        inputs = []
        if req_id in requests:
            inputs = requests[req_id]
        for input in message['parameters']:
            inputs.append(input)
        if util.compare(description['inputs'], inputs):
            user_topic = message['user_topic']
            expected_outputs = message['expected_outputs']
            messages_size = message['messages_size']
            ms = 0.0009
            time.sleep(ms)
            outputs = description['outputs']
            for output in outputs:
                output['value'] = 'Output value from ' + description['name']
                message_dict = {
                    'req_id': req_id, 'user_topic': user_topic, 'expected_outputs': expected_outputs, 'desc': 'message from ' + description['name'] + '_async', 'next_topic': 'service.' + output['name'],
                    'parameters': outputs
                }
                messages_size = messages_size + sys.getsizeof(str(message_dict))
                message_dict['messages_size'] = messages_size
                next_topic = message_dict['next_topic']
                if util.compare_outputs(expected_outputs, outputs):
                    next_topic = user_topic
                    message_dict['next_topic'] = next_topic
                credentials = util.read_rabbit_credentials(rabbit_credentials_file)
                producer = Producer(credentials)
                producer.publish(next_topic, message_dict)
                #producer = Producer(credentials)
                #producer.publish(user_topic, message_dict)
                if req_id in requests:
                    del requests[req_id]
        else:
            requests[req_id] = inputs
            #user_topic = message['user_topic']
            #message_dict = {
            #    'req_id': req_id, 'user_topic': user_topic, 'desc': 'message from ' + description['name'] + '_async ::: ', 'next_topic': user_topic
            #}
            #credentials = util.read_rabbit_credentials(rabbit_credentials_file)
            #producer = Producer(credentials)
            #producer.publish(user_topic, message_dict)
    except Exception as ex:
        user_topic = message['user_topic']
        message_dict = {
                'req_id': req_id, 'user_topic': user_topic, 'desc': 'message from ' + description['name'] + '_async ::: exception: ' + str(ex), 'next_topic': user_topic
        }
        credentials = util.read_rabbit_credentials(rabbit_credentials_file)
        producer = Producer(credentials)
        producer.publish(user_topic, message_dict)


# creates a messages listener per each service input
credentials = util.read_rabbit_credentials(rabbit_credentials_file)
inputs = description['inputs']
for inp in inputs:
    consumer_thread = Consumer(credentials, 'service.' + inp['name'], callback)
    consumer_thread.start()


# flask interface
app = Flask('__name__')


# single endpoint to pass AWS health checks
@app.route('/doa_composition/service_36_async', methods=['GET', 'POST'])
def service_36_async():
    try:
        return make_response({'res': ""})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
