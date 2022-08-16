import pika
import ssl


class Consumer:

    def __init__(self, credentials, binding_key, callback):
        rabbit_url = credentials['rabbitmq_url']
        rabbit_port = credentials['port']
        rabbit_virtual_host = credentials['virtual_host']
        rabbit_credentials = pika.PlainCredentials(credentials['username'], credentials['password'])
        rabbit_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        rabbit_parameters = pika.ConnectionParameters(host=rabbit_url, port=rabbit_port,
                                                      virtual_host=rabbit_virtual_host, credentials=rabbit_credentials,
                                                      ssl_options=pika.SSLOptions(rabbit_context))
        connection = pika.BlockingConnection(rabbit_parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='messages', exchange_type='topic')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='messages', queue=queue_name, routing_key=binding_key)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages...')
        channel.start_consuming()
