import logic.util as util
import logic.square_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import json

credentials = util.read_rabbit_credentials('rabbit-mq.yaml')


def callback(ch, method, properties, body):
    p = None
    message = json.loads(body)
    next_topic = message['next_topic']
    parameters = message['parameters']
    for parameter in parameters:
        if parameter['name'] == 'p':
            p = parameter['value']
    res = logic.square_function(p)
    message_dict = {
        'user_topic': 'user.response', 'desc': 'message from square!!!', 'next_topic': 'user.response',
        'res': logic.square_function(p)
    }
    message_json = json.dumps(message_dict, indent=4)
    producer = Producer(credentials)
    producer.publish(next_topic, message_json)


consumer = Consumer(credentials, 'service.square', callback)
