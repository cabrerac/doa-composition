from flask import Flask, make_response
import logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer
import time
import json
import sys
from logic import util


rabbit_credentials_file = 'rabbit-mq.yaml'


def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    user_topic = message['user_topic']
    expected_output = message['expected_output']
    messages_size = message['messages_size']
    ms = 0.0032
    time.sleep(ms)
    description = util.read_service_description('./description/service_89.json')
    outputs = description['outputs']
    for output in outputs:
        output['value'] = 'Output value from service_89'
    message_dict = {
        'req_id': req_id, 'user_topic': user_topic, 'expected_output': expected_output, 'desc': 'message from service_89_async', 'next_topic': 'service._OUTPUT_SERVICE_89',
        'outputs': outputs
    }
    messages_size = messages_size + sys.getsizeof(str(message_dict))
    message_dict['messages_size'] = messages_size
    next_topic = message_dict['next_topic']
    if expected_output == '_OUTPUT_SERVICE_89':
        next_topic = user_topic
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    producer = Producer(credentials)
    producer.publish(next_topic, message_dict)


credentials = util.read_rabbit_credentials(rabbit_credentials_file)
consumer_thread = Consumer(credentials, 'service._OUTPUT_SERVICE_88', callback)
consumer_thread.start()


# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/service_89_async', methods=['GET', 'POST'])
def service_89_async():
    try:
        return make_response({'res': ""})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
