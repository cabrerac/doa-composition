from flask import Flask, make_response
import pika
import time
from cfn_tools import load_yaml


def _read_rabbit_credentials(file):
    with open(file, 'r') as stream:
        credentials = load_yaml(stream)
        return credentials


# Interfaces
app = Flask('__name__')


@app.route('/doa_composition/home', methods=['GET', 'POST'])
def home():
    return make_response({'res': 'Hello world!!!'})


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
def _home_function():
    return 'Hello world!'


"""@app.route("/doa_composition/request_service", methods=["GET", "POST", "PUT", "DELETE"])
def request_service():
    parameters = request.get_json()
    print("Publishing message...")
    producer = kafka_broker.kafka_producer('add', parameters)


def add(message):
    topic_name = 'add'
    # obtain the last offset value
    consumer, tp = kafka_broker.kafka_consumer(topic_name)
    consumer.seek_to_end(tp)
    lastOffset = consumer.position(tp)
    consumer.seek_to_beginning(tp)
    emit('kafkaconsumer1', {'data': ''})
    for message in consumer:
        print(message)
        emit('kafkaconsumer', {'data': message.value.decode('utf-8')})
        if message.offset == lastOffset - 1:
            break
    consumer.close()


def product(message):
    res = {}
    return res"""
