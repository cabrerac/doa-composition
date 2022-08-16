import logic.util as util
import logic.home_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import time

credentials = util.read_rabbit_credentials('rabbit-mq.yaml')


def callback(ch, method, properties, body):
    msg = body.decode()
    print('Received: ' + msg)
    time.sleep(3)
    producer = Producer(credentials)
    producer.publish('user.response', logic.home_function())


consumer = Consumer(credentials, 'service.home', callback)
