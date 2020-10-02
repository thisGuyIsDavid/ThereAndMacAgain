#!/usr/bin/env python
import pika, sys, os, json
from app.collector.MainProcessor import MainProcessor


def main():
    #   set processor
    main_processor = MainProcessor()

    #   set consumer
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='there_and_mac_again')

    #   set callback
    def callback(ch, method, properties, body):
        received_data = json.loads(body)
        main_processor.process(received_data)

    #   start listening
    channel.basic_consume(queue='there_and_mac_again', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)