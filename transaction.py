from dataclasses import dataclass
import hashlib

@dataclass
class Transaction(object):
    """docstring for Transaction."""

    source: str
    destination: str
    amount: int

    def hash(self):
        return '0x' + hashlib.sha256(str(self).encode('utf-8')).hexdigest()

if __name__ == '__main__':
    transaction = Transaction('123', '321', 90)
