#import blockchain
import time
import transaction



class Block:
    def __init__(self, previousHash, timestamp, nonce=-1):
        ##set

        self.previousHash = previousHash
        self.timestamp = timestamp
        #self.hash
        self.nonce=nonce
        self.listOfTransactions=[]

    def myHash(self):
        #calculate self.hash
        return

    def add_transaction(self, T):
        self.listOfTransactions.append(T)