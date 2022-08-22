from flask import Flask, make_response
import logic.util as util
import logic.home_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import threading
import json


rabbit_credentials_file = 'rabbit-mq.yaml'


#def start_consumer(credentials):
def callback(ch, method, properties, body):
    #ch.close()
    message = json.loads(body)
    req_id = message['req_id']
    next_topic = message['next_topic']
    message_dict = {
        'req_id': req_id, 'user_topic': 'user.response', 'desc': 'response from home!!!',
        'next_topic': 'user.response',
        'res': logic.home_function()
    }
    message_json = json.dumps(message_dict, indent=4)
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    producer = Producer(credentials)
    producer.publish(next_topic, message_json)
    #credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    #consumer_thread = Consumer(credentials, 'service.home', callback)
    #consumer_thread.start()
    #consumer = Consumer(credentials, 'user.response', callback)


credentials = util.read_rabbit_credentials(rabbit_credentials_file)
consumer_thread = Consumer(credentials, 'service.home', callback)
consumer_thread.start()


# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/home_async', methods=['GET', 'POST'])
def home():
    return make_response({'res': logic.home_function()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

"""def callback(ch, method, properties, body):
    time.sleep(5)
    message = json.loads(body)
    req_id = message['req_id']
    next_topic = message['next_topic']
    message_dict = {
        'req_id': req_id, 'user_topic': 'user.response', 'desc': 'response from home!!!', 'next_topic': 'user.response',
        'res': logic.home_function()
    }
    message_json = json.dumps(message_dict, indent=4)
    producer = Producer(credentials)
    producer.publish(next_topic, message_json)


consumer = Consumer(credentials, 'service.home', callback)
"""
