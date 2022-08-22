import pika
import ssl
import threading


class Consumer(threading.Thread):

    def __init__(self, credentials, binding_key, callback):
        threading.Thread.__init__(self)
        rabbit_url = credentials['rabbitmq_url']
        rabbit_port = credentials['port']
        rabbit_virtual_host = credentials['virtual_host']
        rabbit_credentials = pika.PlainCredentials(credentials['username'], credentials['password'])
        rabbit_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        rabbit_parameters = pika.ConnectionParameters(host=rabbit_url, port=rabbit_port,
                                                      virtual_host=rabbit_virtual_host, credentials=rabbit_credentials,
                                                      ssl_options=pika.SSLOptions(rabbit_context))
        self.connection = pika.BlockingConnection(rabbit_parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='messages', exchange_type='topic', durable=True)
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='messages', queue=queue_name, routing_key=binding_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        threading.Thread(target=self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True))
    
    def run(self):
        print(' [*] Waiting for messages...')
        self.channel.start_consuming()
