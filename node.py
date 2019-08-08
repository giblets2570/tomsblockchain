#!/usr/bin/env python
import pika
import json
from transaction import Transaction
from blockchain import Blockchain, solve_blockchain
from block import Block
from account import Account, deserialize_pub_key, verify

BLOCKCHAIN = None
CURRENTBLOCK = Block()
NODEACCOUNT = Account()

def get_blockchain():
    # first try and load it
    try:
        blockchain = Blockchain.load_blockchain()
        return blockchain
    except Exception as e:
        print("No saved blockchain")
        pass

    # then try and fetch it
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()
    channel.exchange_declare(exchange='data-requests', exchange_type='fanout')
    message = json.dumps({
        "type": "blockchain.current",
    })
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.basic_publish(
        exchange='data-requests',
        routing_key='',
        body=message,
        properties=pika.spec.BasicProperties(reply_to=queue_name)
    )

    consumer = channel.consume(queue_name, auto_ack=True, exclusive=True, inactivity_timeout=20)
    for (_, __, data) in consumer:
        channel.cancel()

    if data == None:
        return Blockchain()

    blockchain = Blockchain.deserialize(data)
    return blockchain

def start_consuming_transactions():
    global BLOCKCHAIN
    global CURRENTBLOCK

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange='transactions', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='transactions', queue=queue_name)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        global CURRENTBLOCK
        global BLOCKCHAIN

        data = json.loads(body)
        if data['type'] == 'transaction.new':
            transaction = Transaction.deserialize(data['transaction'])
            pub_key = deserialize_pub_key(data['pub_key'])
            try:
                CURRENTBLOCK.add_transaction(transaction, pub_key, data['signature'])
                print('Transaction added to current block')
            except Exception as e:
                print('Transaction discarded')
                nonce = solve_blockchain(BLOCKCHAIN, CURRENTBLOCK)
                BLOCKCHAIN.add_block(NODEACCOUNT, CURRENTBLOCK, nonce)
                CURRENTBLOCK = Block(BLOCKCHAIN.previous_block_hash)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )
    channel.start_consuming()

def main():
    global BLOCKCHAIN
    BLOCKCHAIN = get_blockchain()
    try:
        start_consuming_transactions()
    except KeyboardInterrupt:
        BLOCKCHAIN.save_blockchain()

if __name__ == '__main__':
    main()
