from flask import Flask, make_response, request
import logic.util as util
import logic.add_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import json


rabbit_credentials_file = 'rabbit-mq.yaml'


def callback(ch, method, properties, body):
    a = None
    b = None
    message = json.loads(body)
    req_id = message['req_id']
    next_topic = message['next_topic']
    parameters = message['parameters']
    for parameter in parameters:
        if parameter['name'] == 'a':
            a = parameter['value']
        if parameter['name'] == 'b':
            b = parameter['value']
    p = logic.add_function(a, b)
    message_dict = {
        'req_id': req_id, 'user_topic': 'user.response', 'desc': 'message from add!!!', 'next_topic': 'user.response',
        'parameters': [
            {'name': 'p', 'value': p}
        ]
    }
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    producer = Producer(credentials)
    producer.publish(next_topic, message_dict)


credentials = util.read_rabbit_credentials(rabbit_credentials_file)
consumer_thread = Consumer(credentials, 'service.add', callback)
consumer_thread.start()


# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/add_async', methods=['GET', 'POST'])
def add():
    try:
        parameters = request.get_json()
        a = parameters['s1']
        b = parameters['s2']
        return make_response({'res': logic.add_function(a, b)})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
