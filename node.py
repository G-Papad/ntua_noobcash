import block
import wallet
import transaction
import json
from flask import Flask, jsonify, request, render_template
import requests

log = []

class Node:
	def __init__(self):
		self.NBC=100
		##set

		#self.chain
		self.current_id_count = 0
		self.wallet = self.create_wallet()
		# self.NBCs 
		self.ring = {self.wallet.address : [0, '127.0.0.1:5000', self.NBC]} # here we store information for every node, as its id, its address (ip:port) its public key and its balance 

	def create_new_block():
		return

	def create_wallet(self):
		return wallet.Wallet()

	def register_node_to_ring(self, public_key, ip):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		self.current_id_count += 1
		self.ring[self.wallet.address][2] += 100
		self.ring[public_key] = [self.current_id_count, ip, 0]		
		return self.ring

	def create_transaction(self, receiver, amount):
		#remember to broadcast it
		s = 0
		transactionInputs = []
		for t in self.wallet.utxos:
			if s >= amount: break
			if t.address == self.wallet.address: 
				transactionInputs.append(t)
				s += t.amount
		self.broadcast_transaction(transaction.Transaction(self.wallet.public_key, receiver, amount, self.wallet.private_key, transactionInputs))


	def broadcast_transaction(self, T):
		
		log.append(T)
		dic = T.to_dict()

		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip + '/'
			data = json.dumps(dic)
			res = requests.post(url + 'broadcast', json = data)


	def receive(self):
		newT = log[0]
		self.validate_transaction(newT)
		for x in newT.transaction_inputs:
			for y in self.wallet.utxos: 
				if x.transaction_id == y.transaction_id and x.address == y.address and x.amount == y.amount:
					self.wallet.utxos.remove(y)
					if x.address in self.ring: 						# update ring dict
						self.ring[x.address][2] -= x.amount
					else: 
						print("Something went wrong with NBCs dict")

		for x in newT.transaction_outputs:
			self.wallet.utxos.append(x)
			self.ring[x.address][2] += x.amount

		for x in newT.transaction_inputs:
			print("Input:\n")
			x.print_trans()
		for x in newT.transaction_outputs:
			print("Output:\n")
			x.print_trans()
		for x in self.wallet.utxos:
			print("Wallet:")
			x.print_trans()

	def validate_transaction(self, T):
		#use of signature and NBCs balance
		if T.hash() != T.transaction_id:
			print("Error: Wrong hash!\n")
			return False
		if not T.verify_signature(): 
			print("Error: Wrong signature!\n")
			return False
		# also check for enough balance
		return True



	# def add_transaction_to_block():
	# 	#if enough transactions  mine



	# def mine_block():



	# def broadcast_block():


		

	# def valid_proof(.., difficulty=MINING_DIFFICULTY):




	# #concencus functions

	# def valid_chain(self, chain):
	# 	#check for the longer chain accroose all nodes


	# def resolve_conflicts(self):
	# 	#resolve correct chain



