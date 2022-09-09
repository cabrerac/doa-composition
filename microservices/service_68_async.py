from flask import Flask, make_response
import logic.util as util
from clients.producer import Producer
from clients.consumer import Consumer
import time
import json


rabbit_credentials_file = 'rabbit-mq.yaml'


def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    user_topic = message['user_topic']
    expected_output = message['expected_output']
    ms = 0.002
    time.sleep(ms)
    message_dict = {
        'req_id': req_id, 'user_topic': user_topic, 'expected_output': expected_output, 'desc': 'message from service_68_async', 'next_topic': 'service._OUTPUT_SERVICE_68',
        'parameters': [
            {'name': 'p', 'value': 'Response from service_68_async'}
        ]
    }
    next_topic = message_dict['next_topic']
    if expected_output == '_OUTPUT_SERVICE_68':
        next_topic = user_topic
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    producer = Producer(credentials)
    producer.publish(next_topic, message_dict)


credentials = util.read_rabbit_credentials(rabbit_credentials_file)
consumer_thread = Consumer(credentials, 'service._OUTPUT_SERVICE_67', callback)
consumer_thread.start()


# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/service_68_async', methods=['GET', 'POST'])
def service_68_async():
    try:
        return make_response({'res': ""})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
