import block
import wallet
import transaction
import json
from flask import Flask, jsonify, request, render_template
import requests
import time
import blockchain

#####################################
# [TO FIX]: Implement in BlockChain
#####################################

CAPACITY = 1
port = ':5000'

class Node:
	def __init__(self, master=False, N=None):
		self.wallet = self.create_wallet()
		self.doMine = False
		self.chain = blockchain.BlockChain(capacity=CAPACITY)
		if(master):
			self.NBC=100*N
			self.id = 0
			self.current_id_count = 1 #id for the next node
			self.ring = {self.wallet.address.decode() : [0, '192.168.1.4']} # here we store information for every node, as its id, its address (ip:port) its public key and its balance 
			genesis_block = block.Block(1,time.time(), 0)
			genesis_transaction = transaction.Transaction(0, self.wallet.address, self.NBC,[])
			genesis_block.add_transaction(genesis_transaction)
			self.chain.add_block(genesis_block)
		else:
			self.id=-1
			self.ring={}	
			self.block = self.create_new_block()

	def create_new_block(self):
		self.doMine = False
		self.block = block.Block(0,0)

	def create_wallet(self):
		return wallet.Wallet()

	def register_node_to_ring(self, public_key, ip):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		if(self.id==0):
			print(type(public_key))
			if public_key in self.ring.keys():
				requests.post('http://'+ip+port+'/registerFail', json={'ERROR' : 'Public address already in use!'})
			else:
				self.ring[public_key] = [self.current_id_count, ip]
				for _, value in self.ring.items():
					print(type(_))
					ip_b = value[1]
					url_newNode = 'http://'+ip_b+port+'/broadcastNewNode'
					requests.post(url_newNode, json={'ring' : self.ring})
				self.current_id_count+=1

				self.create_transaction(receiver=public_key, amount=100)
				url_newNode = 'http://'+ip+port+'/broadcastBlockChain'
				json_blockchain = self.chain.to_dict()
				requests.post(url_newNode, json=json_blockchain)
		return

	def create_transaction(self, receiver, amount):
		#remember to broadcast it
		s = 0
		transactionInputs = []
		for t in self.wallet.utxos:
			if s >= amount: break
			if t.address == self.wallet.address: 
				transactionInputs.append(t)
				s += t.amount
		self.broadcast_transaction(transaction.Transaction(self.wallet.public_key, receiver, amount, transactionInputs, self.wallet.private_key))

	def broadcast_transaction(self, T):
		
		dic = T.to_dict()

		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip + '/'
			# data = json.dumps(dic)
			res = requests.post(url + 'broadcastTransaction', json = dic)

	def run_transaction(self, T):
		transaction_inputs = T.transaction_inputs
		transaction_outputs = T.transaction_outputs

		for t_in in transaction_inputs:
			for t in self.wallet.utxos:
				if t_in.transaction_id == t.transaction_id :
					self.wallet.utxos.remove(t)
		
		for t_out in transaction_outputs:
			self.wallet.utxos.append(t_out)
			
	def validate_transaction(self, T):
		#use of signature and NBCs balance
		# if T.hash() != T.transaction_id:
		# 	print("Error: Wrong hash!\n")
		# 	return False
		if not T.verify_signature(): 
			print("Error: Wrong signature!\n")
			return False
		# also check for enough balance
		# Should we check for enough balance or for same transaction inputs?
		transaction_inputs = T.transaction_inputs

		if transaction_inputs == []:
			return False

		for t_in in transaction_inputs:
			res = False 
			for t_utxo in self.wallet.utxos:
				if t_in.transaction_id == t_utxo.transaction_id:
					res = True
			if res == False:
				return False
			
		return True



	def add_transaction_to_block(self, T):
		# if enough transactions  mine
		if(self.doMine == False):
			self.block.add_transaction(T)
			if(len(self.block.listOfTransactions) == CAPACITY):
				self.doMine = True
				self.mine_block()
		else:
			return


	def mine_block(self):
		#do later
		return



	# def broadcast_block():


		

	# def valid_proof(.., difficulty=MINING_DIFFICULTY):




	# #concencus functions

	# def valid_chain(self, chain):
	# 	#check for the longer chain across all nodes


	# def resolve_conflicts(self):
	# 	#resolve correct chain



