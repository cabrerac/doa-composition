import logic.util as util
import logic.home_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import time
import json

credentials = util.read_rabbit_credentials('rabbit-mq.yaml')


def callback(ch, method, properties, body):
    time.sleep(5)
    message = json.loads(body)
    next_topic = message['next_topic']
    message_dict = {
        'user_topic': 'user.response', 'desc': 'response from home!!!', 'next_topic': 'user.response',
        'res': logic.home_function()
    }
    message_json = json.dumps(message_dict, indent=4)
    producer = Producer(credentials)
    producer.publish(next_topic, message_json)


consumer = Consumer(credentials, 'service.home', callback)
