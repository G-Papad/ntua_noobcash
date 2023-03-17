from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

#import requests
from flask import Flask, jsonify, request, render_template

class TransactionIO:

    def __init__(self, transaction_id, address, amount):
        self.transaction_id = transaction_id
        self.address = address
        self.amount = amount
        

class Transaction:

    def __init__(self, sender_address, receiver_address, amount, sender_private_key, transactionInputs):
    
        self.sender_address = sender_address # To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = receiver_address # To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = amount # το ποσό που θα μεταφερθεί
        self.transaction_id = self.hash() # το hash του transaction
        self.transaction_inputs = transactionInputs # λίστα από Transaction Input
        change = amount - sum([x.amount for x in transactionInputs])
        self.transaction_outputs = [TransactionIO(self.transaction_id, sender_address, change), 
                                    TransactionIO(self.transaction_id, receiver_address, amount)] # λίστα από Transaction Output 
        self.Signature = self.sign_transaction(sender_private_key)

    def to_dict(self):
        return
    
    def hash(self):
        return 0

    def sign_transaction(self, sender_private_key):
        # Sign transaction with private key
        return
       