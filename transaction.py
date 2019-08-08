from dataclasses import dataclass
import hashlib
import json

@dataclass
class Transaction(object):
    """docstring for Transaction."""

    source: str
    destination: str
    amount: int

    @property
    def hash(self):
        return '0x' + hashlib.sha256(str(self).encode('utf-8')).hexdigest()

    def serialize(self):
        return {
            "source": self.source,
            "destination": self.destination,
            "amount": self.amount,
        }

    @classmethod
    def deserialize(cls, data):
        if type(data) == dict:
            return cls(**data)
        kwargs = json.loads(data)
        return cls(**kwargs)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Transaction):
            return (
                self.source == other.source and
                self.destination == other.destination and
                self.amount == other.amount
            )
        return False

if __name__ == '__main__':
    transaction = Transaction('123', '321', 90)
    data = transaction.serialize()
    t = Transaction.deserialize(data)
    assert t == transaction
