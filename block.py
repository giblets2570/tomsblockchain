import hashlib
import json
from dataclasses import dataclass, field
from typing import List
from transaction import Transaction
from account import generate_address, verify
@dataclass
class Block(object):
    """docstring for Block."""

    previous_block_hash: str = '0x' + '0' * 64
    leafs: List[str] = field(default_factory=list)
    root: str = ""
    transactions: List[Transaction] = field(default_factory=list)
    max_transactions: int = 4
    complete: bool = False
    nonce: int = 0 # to prove

    @property
    def hash(self):
        return '0x' + hashlib.sha256(str(self).encode('utf-8')).hexdigest()

    def serialize(self):
        return {
            "previous_block_hash": self.previous_block_hash,
            "leafs": self.leafs,
            "root": self.root,
            "transactions": [t.serialize() for t in self.transactions],
            "max_transactions": self.max_transactions,
            "complete": self.complete,
            "nonce": self.nonce,
        }

    @classmethod
    def deserialize(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)

    def add_transaction(self, transaction, pub_key, signature):
        if len(self.transactions) >= self.max_transactions:
            raise Exception("Block is full")

        if transaction.source != generate_address(pub_key):
            raise Exception("Cannot sign transactions for other users")

        if not verify(transaction.hash, pub_key, signature):
            raise Exception("Signature doesn't match public key")

        self.transactions.append(transaction)
        self._generate_merkle_tree()

    def _generate_merkle_tree(self):
        base_leafs = []
        for i in range(self.max_transactions):
            if len(self.transactions) < i + 1:
                base_leafs.append('0x' + '0' * 64)
            else:
                transaction = self.transactions[i]
                base_leafs.append(transaction.hash)

        leafs = [base_leafs]

        while len(leafs[-1]) > 1:
            next_leafs = []
            for i in range(0, len(leafs[-1]), 2):
                combined_hashes = leafs[-1][i] + leafs[-1][i+1]
                next_hash = '0x'+hashlib.sha256(combined_hashes.encode('utf-8')).hexdigest()
                next_leafs.append(next_hash)
            leafs.append(next_leafs)

        self.leafs = leafs
        self.root = leafs[-1][-1]

if __name__ == '__main__':
    from account import Account

    alice = Account()
    bob = Account()
    block = Block()

    # next block of transactions
    transaction = Transaction(bob.address, alice.address, 50)
    signature = bob.sign(transaction.hash)
    block.add_transaction(transaction, bob.pub_key, signature)

    print(block.serialize())
