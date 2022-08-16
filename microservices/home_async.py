import logic.util as util
import logic.home_function as logic
from clients.producer import Producer
from clients.consumer import Consumer

credentials = util.read_rabbit_credentials('rabbit-mq.yaml')


def callback(ch, method, properties, body):
    msg = body.decode()
    print('Received: ' + msg)
    producer = Producer(credentials)
    producer.publish('user.response', 'response from service!!!')


consumer = Consumer(credentials, 'service.home', callback)
