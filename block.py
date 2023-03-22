#import blockchain
import time
import transaction
from Crypto.Hash import SHA256
import json

class Block:
    def __init__(self, previousHash, timestamp, nonce=-1,tlist=[]):
        ##set

        self.previousHash = previousHash
        self.timestamp = timestamp
        self.nonce=nonce
        self.listOfTransactions=tlist
        self.hash = None

    def myHash(self):
        dic_blck = self.to_dict()
        del dic_blck['hash']
        block_to_byte = json.dumps(dic_blck).encode()
        return SHA256.new(block_to_byte).hexdigest()

    def add_transaction(self, T):
        self.listOfTransactions.append(T)
        return

    def to_dict(self):
        block = {
            'previousHash' : self.previousHash,
            'timestamp' : self.timestamp,
            'hash' : self.hash,
            'nonce' : self.nonce,
            'listOfTransactions' : [x.to_dict() for x in self.listOfTransactions]
        }
        return block