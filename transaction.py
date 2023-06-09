from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import hashlib
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA

import json
import jsonpickle
from json import JSONEncoder
#import requests
from flask import Flask, jsonify, request, render_template

import base64

class TransactionIO:

    def __init__(self, transaction_id, address, amount):
        self.address = address
        self.amount = amount
        # bytes_to_hash = bytes(transaction_id + address.decode() +str(amount), 'utf-8')
        # self.transaction_id = SHA256.new(bytes_to_hash).hexdigest()
        self.transaction_id = transaction_id
        
    
    def print_trans(self):
        print("TransactionIO: ", self.transaction_id, ", ", self.address, ", ", self.amount, "\n")
        
    def toString(self):
        return [self.transaction_id, self.address.decode(), str (self.amount)]

class Transaction:

    def __init__(self, sender_address, receiver_address, amount, transactionInputs, sender_private_key = None, signature=None):
    
        self.sender_address = sender_address # To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = receiver_address # To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = amount # το ποσό που θα μεταφερθεί
        self.transaction_inputs = transactionInputs # λίστα από Transaction Input
        self.transaction_id = self.hash() # το hash του transaction
        change = sum([x.amount for x in transactionInputs]) - amount
        self.transaction_outputs = [TransactionIO(self.transaction_id.hexdigest(), sender_address, change), 
                                    TransactionIO(self.transaction_id.hexdigest(), receiver_address, amount)] # λίστα από Transaction Output 
        if (sender_private_key != None): 
            self.signature = self.sign_transaction(sender_private_key)
        else:
            self.signature = signature

    def to_dict(self):
        
        transactions = {
            'sender_address' : self.sender_address.decode(),
            'receiver_address' : self.receiver_address.decode(),
            'amount' : self.amount,
            'transaction_id' : self.transaction_id.hexdigest(),
            'transaction_inputs' : [x.toString() for x in self.transaction_inputs],
            'transaction_outputs' : [x.toString() for x in self.transaction_outputs],
            'signature' : base64.b64encode(self.signature).decode()
        }

        return transactions
    
    def hash(self):
        #calculate self.hash
        tr_inputs = str(jsonpickle.encode(self.transaction_inputs))
        block_to_byte = bytes(str(self.sender_address) + str(self.receiver_address) + str(self.amount) + tr_inputs, 'utf-8')
        return SHA256.new(block_to_byte)

    def sign_transaction(self, sender_private_key):
        """
        Sign transaction with private key
        """
        signer = pkcs1_15.new(RSA.import_key(sender_private_key))
        return signer.sign(self.transaction_id)
    
    def print_trans(self):
        print("TransactionIO: ", self.transaction_id, ", ", self.sender_address, ", ", self.receiver_address, ", ", self.amount, "\n")
    
    def verify_signature(self):
        pk = RSA.import_key(self.sender_address)
        verifier = PKCS1_v1_5.new(pk)
        return verifier.verify(self.transaction_id, self.signature)
   