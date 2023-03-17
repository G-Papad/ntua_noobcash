import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import transaction



class wallet:

	def __init__(self):

		rsaKeys = RSA.generate(2048)
		self.public_key = rsaKeys.publickey().exportKey('PEM')
		self.private_key = rsaKeys.exportKey('PEM')
		self.address = self.public_key
		self.utxos = []

	def balance(self):
		return sum([x.amount for x in self.utxos if x.address == self.address])
