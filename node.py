import block
import wallet
import transaction
import json
from flask import Flask, jsonify, request, render_template
import requests
import time
import blockchain
import Crypto.Random

#####################################
# [TO FIX]: Implement in BlockChain
#####################################

CAPACITY = 3
MINING_DIFFICULTY = 4
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
			genesis_block = block.Block(1,time.time(), nonce=0)		
			genesis_transaction = transaction.Transaction(b'0', self.wallet.address, self.NBC,[],signature=b'notvalid_signature_bozo')		
			genesis_block.add_transaction(genesis_transaction)
			genesis_block.hash = genesis_block.myHash()
			self.run_transaction(genesis_transaction)
			self.chain.add_block(genesis_block)
			self.create_new_block(genesis_block.hash)
		else:
			self.id=-1
			self.ring={}	
			self.block = None

	def create_new_block(self, prevHash):
		self.doMine = False
		self.block = block.Block(prevHash,time.time())

	def create_wallet(self):
		return wallet.Wallet()

	def register_node_to_ring(self, public_key, ip):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		if(self.id==0):
			# print(type(public_key))
			if public_key in self.ring.keys():
				requests.post('http://'+ip+port+'/registerFail', json={'ERROR' : 'Public address already in use!'})
			else:
				self.ring[public_key] = [self.current_id_count, ip]
				for _, value in self.ring.items():
					# print(type(_))
					ip_b = value[1]
					url_newNode = 'http://'+ip_b+port+'/broadcastNewNode'
					requests.post(url_newNode, json={'ring' : self.ring})
				self.current_id_count+=1

				url_newNode = 'http://'+ip+port+'/broadcastBlockChain'
				blockchain = self.chain.to_dict()
				requests.post(url_newNode, json=blockchain)

				self.create_transaction(receiver=public_key.encode(), amount=100)
		
		return

	def create_transaction(self, receiver, amount):
		#remember to broadcast it
		s = 0
		transactionInputs = []

		# [To Think?!] : Do we really need this flag?
		# flag = False
		
		for t in self.wallet.utxoslocal:
			if s >= amount:
				# flag = True 
				break
			if t.address == self.wallet.address: 
				transactionInputs.append(t)
				s += t.amount
		
		trans = transaction.Transaction(self.wallet.public_key, receiver, amount, transactionInputs, self.wallet.private_key)
		self.broadcast_transaction(trans)
		
		return transaction

	def broadcast_transaction(self, T):
		
		dic = T.to_dict()

		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip +port+ '/'
			# data = json.dumps(dic)
			res = requests.post(url + 'broadcastTransaction', json = dic)

	def run_blockchain(self):
		self.wallet.utxos = []
		# i=1
		# print("UTXOs before running BlockChain:")
		# for x in self.wallet.utxos:
		# 	x.print_trans()
		for b in self.chain.blocks:
			self.block = b
			# print("Running Block number ", i)
			self.run_block()
			# i += 1
		# print("UTXOs after running BlockChain:")
		# for x in self.wallet.utxos:
		# 	x.print_trans()


	def run_block(self):
		for t in self.block.listOfTransactions:
			self.run_transaction(t)
		self.wallet.utxoslocal = self.wallet.utxos.copy()


	def run_transaction_local(self, T):
		transaction_inputs = T.transaction_inputs
		transaction_outputs = T.transaction_outputs

		for t_in in transaction_inputs:
			temp = self.wallet.utxoslocal.copy()
			for t in temp:
				if t_in.transaction_id == t.transaction_id and t_in.address == t.address and t_in.amount == t.amount:
					self.wallet.utxoslocal.remove(t)
		
		for t_out in transaction_outputs:
			self.wallet.utxoslocal.append(t_out)
			

	def run_transaction(self, T):
		transaction_inputs = T.transaction_inputs
		transaction_outputs = T.transaction_outputs

		for t_in in transaction_inputs:
			temp = self.wallet.utxos.copy()
			for t in temp:
				if t_in.transaction_id == t.transaction_id and t_in.address == t.address and t_in.amount == t.amount:
					self.wallet.utxos.remove(t)
		
		for t_out in transaction_outputs:
			self.wallet.utxos.append(t_out)
		
		self.wallet.utxoslocal = self.wallet.utxos.copy()
			
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
			print("[Iteration Start]---------------------------------")
			for t_utxo in self.wallet.utxoslocal:
				print("\t\t\t----------------START-----------------")
				t_utxo.print_trans()
				print("\t\t\t---------------------------------")
				t_in.print_trans()
				print("\t\t\t----------------END-----------------")
				if t_in.transaction_id == t_utxo.transaction_id and t_in.address == t_utxo.address and t_in.amount == t_utxo.amount:
					res = True
			if res == False:
				print("Wut boy?!")
				return False
			print("[Iteration End]---------------------------------")
			
		return True



	def add_transaction_to_block(self, T):
		# if enough transactions  mine
		if(self.doMine == False):
			self.block.add_transaction(T)
			self.run_transaction_local(T)
			print(len(self.block.listOfTransactions),' of ', CAPACITY)
			if(len(self.block.listOfTransactions) == CAPACITY):
				self.doMine = True
				self.mine_block()
		else:
			return

	def mine_block(self):
		while self.doMine == True:
			self.block.hash = self.block.myHash()
			if self.valid_proof(self.block.hash):
				self.doMine = False
				self.broadcast_block()
				break
			else:
				self.block.nonce = Crypto.Random.random.getrandbits(32)
		return

	def broadcast_block(self):
		dic_blck = self.block.to_dict()
		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip + port + '/'
			# data = json.dumps(dic)
			res = requests.post(url + 'broadcastBlock', json = dic_blck)
		return

	def valid_proof(self, hash, difficulty=MINING_DIFFICULTY):
		i=0
		res = True
		while i < difficulty:
			if hash[i] != '0':
				res = False
				break
			i += 1
		return res

	def validate_block(self, B:block.Block):
		if not self.valid_proof(B.hash):
			return False
		for t in B.listOfTransactions:
			if not self.validate_transaction(t):
				return False
			self.run_transaction_local(t)
		return True
	
	def reverse_transaction(self, T):
		transaction_inputs = T.transaction_inputs
		transaction_outputs = T.transaction_outputs

		for t_in in transaction_outputs:
			temp = self.wallet.utxoslocal.copy()
			for t in temp:
				if t_in.transaction_id == t.transaction_id and t_in.address == t.address and t_in.amount == t.amount:
					self.wallet.utxoslocal.remove(t)
		
		for t_out in transaction_inputs:
			self.wallet.utxoslocal.append(t_out)

	def reverse_blocks_until_conflict(self, conflict_hash):
		for b in reversed(self.chain.blocks):
			if b.hash == conflict_hash:
				break
			else:
				for t in b.listOfTransactions:
					self.reverse_transaction(t)
		return

	def validate_chain(self, chain, conflict_hash):
		current_hash = conflict_hash
		restore_point = self.wallet.utxoslocal.copy()
		self.wallet.utxoslocal = self.wallet.utxos.copy()
		self.reverse_blocks_until_conflict(conflict_hash)
		for b in chain:
			if not (self.validate_block(b) and b.previousHash == current_hash):
				self.wallet.utxoslocal = restore_point.copy()
				return False
			current_hash = b.hash
		return True


	# #concencus functions

	def valid_chain(self, chain):
		#check for the longer chain across all nodes
		chain_length = len(self.chain.blocks)
		hashes = [x.hash for x in self.chain.blocks]
		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip + port + '/'
			# data = json.dumps(dic)
			res = requests.post(url + 'broadcastvalidChain', 
		       json = {'length': chain_length , 'hashes': hashes})
		return


	def resolve_conflicts(self):
		# resolve correct chain

		return



