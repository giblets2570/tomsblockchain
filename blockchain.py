from dataclasses import dataclass, field
from typing import List, Dict
from transaction import Transaction
from account import generate_address
from block import Block
import hashlib

@dataclass
class Blockchain(object):
    """docstring for Blockchain."""

    blocks: List[Block] = field(default_factory=list)
    difficulty: int = 2
    block_reward: int = 50
    previous_block_hash: str = '0x' + '0' * 64
    ledger: Dict[str, int] = field(default_factory=dict)

    def solve_puzzle(self, block, nonce):
        if block.previous_block_hash != self.previous_block_hash:
            raise Exception("Wrong previous block hash")

        message = self.previous_block_hash + block.hash() + str(nonce)
        message_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
        solved = all([c == '0' for c in message_hash[:self.difficulty]])
        return solved

    def add_block(self, account, block, nonce):
        if not self.solve_puzzle(block, nonce):
            raise Exception("Block doesnt fit")

        # We check if all the transactions are valid
        # now we update the ledger
        for transaction in block.transactions:
            if transaction.source not in self.ledger:
                self.ledger[transaction.source] = 0
            if self.ledger[transaction.source] < transaction.amount:
                raise Exception("Not enough balance")

        block.nonce = nonce
        block.complete = True
        self.blocks.append(block)
        self.previous_block_hash = block.hash()

        # now we update the ledger
        for transaction in block.transactions:
            if transaction.destination not in self.ledger:
                self.ledger[transaction.destination] = 0

            self.ledger[transaction.source] -= transaction.amount
            self.ledger[transaction.destination] += transaction.amount


        address = generate_address(account.pub_key)
        if address not in self.ledger:
            self.ledger[address] = 0
        self.ledger[address] += self.block_reward

def solve_blockchain(blockchain, block):
    # client trying to solve the puzzle
    solved = False
    i = -1
    while not solved:
        i += 1
        solved = blockchain.solve_puzzle(block, i)

    return i

if __name__ == '__main__':
    from account import Account

    alice = Account()
    bob = Account()

    blockchain = Blockchain()
    block = Block()

    # client trying to solve the puzzle
    correct_nonce = solve_blockchain(blockchain, block)

    blockchain.add_block(bob, block, correct_nonce)

    # next block of transactions
    transaction = Transaction(bob.address, alice.address, 50)

    block = Block(blockchain.blocks[-1].hash())
    signature = bob.sign(transaction.hash())
    block.addTransaction(transaction, bob.pub_key, signature)

    # client trying to solve the puzzle
    correct_nonce = solve_blockchain(blockchain, block)

    blockchain.add_block(alice, block, correct_nonce)
