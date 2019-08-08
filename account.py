from dataclasses import dataclass
import hashlib
from fastecdsa import keys, curve, ecdsa, point

def hex_number(number, number_bytes=32):
    result = hex(number)[2:]
    while len(result) < number_bytes * 2:
        result = '0' + result
    return result

def generate_keypair():
    priv_key, pub_key = keys.gen_keypair(curve.secp256k1)
    return priv_key, pub_key

def serialize_pub_key(pub_key):
    return keys.export_key(pub_key, curve=curve.secp256k1)

def deserialize_pub_key(pub_key_str):
    return keys.PEMEncoder.decode_public_key(pub_key_str, curve=curve.secp256k1)

def generate_address(pub_key, address_bytes=20):
    concat_pub = hex_number(pub_key.x) + hex_number(pub_key.y)
    concat_pub_bytes = bytes.fromhex(concat_pub)
    m = hashlib.sha256()
    m.update(concat_pub_bytes)
    address = '0x' + m.hexdigest()[-2*address_bytes:]
    return address

def verify(message, pub_key, signature):
    signature_length = len(signature)
    half = signature_length // 2
    r = int(signature[:half], 16)
    s = int(signature[half:], 16)
    valid = ecdsa.verify((r, s), message, pub_key, curve=curve.secp256k1)
    return valid


@dataclass
class Account(object):
    """docstring for Account."""

    priv_key: int
    pub_key: point.Point
    address: str

    @property
    def pub_key_str(self):
        return serialize_pub_key(self.pub_key)
        
    def __init__(self, priv_key=None):
        if priv_key == None:
            self.priv_key, self.pub_key = generate_keypair()
        else:
            self.priv_key = priv_key
            self.pub_key = keys.get_public_key(self.priv_key, curve.secp256k1)
        self.address = generate_address(self.pub_key)

    def sign(self, message):
        r, s = ecdsa.sign(message, self.priv_key, curve=curve.secp256k1)
        signature = hex_number(r) + hex_number(s)
        return signature

if __name__ == '__main__':
    toms_account = Account()

    # message = "pears"
    # signature = toms_account.sign(message)
    # valid = verify(message, toms_account.pub_key, signature)

    print(toms_account.pub_key)
    s = serialize_pub_key(toms_account.pub_key)
    p = deserialize_pub_key(s)

    print(p)
