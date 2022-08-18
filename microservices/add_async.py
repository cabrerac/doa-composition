import logic.util as util
import logic.add_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import json

credentials = util.read_rabbit_credentials('rabbit-mq.yaml')


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
    message_json = json.dumps(message_dict, indent=4)
    producer = Producer(credentials)
    producer.publish(next_topic, message_json)


consumer = Consumer(credentials, 'service.add', callback)
