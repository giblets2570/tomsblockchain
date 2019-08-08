#!/usr/bin/env python
import pika
import sys
import json
from transaction import Transaction
from account import Account

alice = Account(5998553955444540460096877707037083734544407047745296628850716194378212841918)
bob = Account(86001130041322989482485144622702459429430532327524027045548591725405801461157)

def send_transaction():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange='transactions', exchange_type='fanout')

    transaction = Transaction(alice.address, bob.address, 0)
    signature = alice.sign(transaction.hash)
    pub_key = alice.pub_key_str

    message = json.dumps({
        "type": "transaction.new",
        "pub_key": pub_key,
        "transaction": transaction.serialize(),
        "signature": signature,
    })
    channel.basic_publish(exchange='transactions', routing_key='', body=message)

    print(" [x] Sent %r" % message)

    connection.close()

if __name__ == '__main__':
    send_transaction()
