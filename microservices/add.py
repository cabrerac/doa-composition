from flask import Flask, make_response, request
import pika
import time
from cfn_tools import load_yaml


def _read_rabbit_credentials(file):
    with open(file, 'r') as stream:
        credentials = load_yaml(stream)
        return credentials


# Interfaces
app = Flask('__name__')


@app.route('/doa_composition/add', methods=['GET', 'POST'])
def add():
    parameters = request.get_json()
    a = parameters['s1']
    b = parameters['s2']
    return make_response({'res': _add_function(a, b)})


sleepTime = 10
time.sleep(30)

credentials = _read_rabbit_credentials('rabbit-mq.yaml')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=credentials['host']))
channel = connection.channel()
channel.queue_declare(queue='task_square', durable=True)


def _callback(ch, method, properties, body):
    msg = body.decode()

    if msg == 'hey':
        print("hey there")
    elif msg == 'hello':
        print("well hello there")
    else:
        print("sorry i did not understand ", body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_square', on_message_callback=_callback)
channel.start_consuming()


def _publish_message(msg, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=msg,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ))
    connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# Function
def _add_function(a, b):
    return a + b
