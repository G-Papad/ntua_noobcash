from block import Block
import wallet
import transaction
import json
from flask import Flask, jsonify, request, render_template
import requests
import time
import blockchain
from Crypto.Random import random
import threading
import termcolor as co
import base64

#####################################
# [TO FIX]: Implement in BlockChain
#####################################

CAPACITY = 3
MINING_DIFFICULTY = 3
port = ':5000'
ip = '192.168.1.4'
master_ip = '192.168.1.4'

class Node:
	def __init__(self, master=False, N=None):
		self.transaction_pool = []
		self.wallet = self.create_wallet()
		self.doMine = threading.Event()
		self.block_run = threading.Event()
		self.chain = blockchain.BlockChain(capacity=CAPACITY)
		self.mine_thread = threading.Thread(target = self.nope)
		self.block_thread = threading.Thread(target = self.nope)
		if(master):
			self.block = None
			self.NBC=100*N
			self.id = 0
			self.current_id_count = 1 #id for the next node
			self.ring = {self.wallet.address.decode() : [0, '192.168.1.4']}
			# here we store information for every node, as its id, its address (ip:port) its public key and its balance 
			genesis_transaction = transaction.Transaction(b'0', self.wallet.address, 
						 self.NBC, [], sender_private_key = None, signature=b'notvalid_signature_bozo')
			genesis_block = Block(1,time.time(), nonce=0, tlist=[genesis_transaction])						
			# genesis_block.add_transaction(genesis_transaction)
			self.run_transaction(genesis_transaction)
			self.chain.add_block(genesis_block)
			ghash = genesis_block.hash
			self.create_new_block(ghash)
		else:
			self.id=-1
			self.ring={}	
			self.block = None
			self.doMine.clear()
		
		run_trans = threading.Thread(target=self.run_trans_from_txt, daemon=True)
		run_trans.start()

	def nope (self):
		return
	
	def add_transaction_to_pool(self, T):
		self.transaction_pool.append(T)
		print('Transaction added to pool')
		return

	def create_new_block(self, prevHash):
		self.block = Block(prevHash,time.time(), nonce=-1, tlist=[])
		self.block_run.set()
		print(self.block.previousHash)
		self.block_thread = threading.Thread(target = self.add_transaction_to_block, daemon=True)
		self.block_thread.start()
		# return self.block

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
		
		return trans

	def broadcast_transaction(self, T):
		
		dic = T.to_dict()
		print("[Transaction]: Broadcasting ...")
		print("\tTransaction: ", dic)
		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip +port+ '/'
			# data = json.dumps(dic)
			res = requests.post(url + 'broadcastTransaction', json = dic)
		print("[Transaction]: END")
	
	def run_blockchain(self):
		self.wallet.utxos = []
		# i=1
		# print("UTXOs before running BlockChain:")
		# for x in self.wallet.utxos:
		# 	x.print_trans()
		for b in self.chain.blocks:
			# print("Running Block number ", i)
			self.run_block(b)
			# i += 1
		# print("UTXOs after running BlockChain:")
		# for x in self.wallet.utxos:
		# 	x.print_trans()


	def run_block(self,B):
		b = B.copy()
		for t in b.listOfTransactions:
			self.run_transaction(t)
		self.wallet.utxoslocal = self.wallet.utxos.copy()


	def run_transaction_local(self, T):
		transaction_inputs = T.transaction_inputs
		transaction_outputs = T.transaction_outputs
		print("[DEBUGGING RUN TRANSACTION LOCAL]")
		print("\n")
		print("Before UTXOs Local:")
		print("\n")
		print("\t------------------------------------")
		for x in self.wallet.utxoslocal:
			x.print_trans()
			print("\t------------------------------------")
		print("\n")
		print("\tTransactions Inputs:")
		print("\n")
		print("\t------------------------------------")
		for x in transaction_inputs:
			x.print_trans()
			print("\t------------------------------------")
		print("\n")
		print("\tTransactions Outputs:")
		print("\n")
		print("\t------------------------------------")
		for x in transaction_outputs:
			x.print_trans()
			print("\t------------------------------------")
		
		for t_in in transaction_inputs:
			temp = self.wallet.utxoslocal.copy()
			for t in temp:
				if t_in.transaction_id == t.transaction_id and t_in.address == t.address and t_in.amount == t.amount:
					self.wallet.utxoslocal.remove(t)
					break
		
		for t_out in transaction_outputs:
			if (t_out.amount > 0):
				self.wallet.utxoslocal.append(t_out)

		print("Current UTXOs Local:")
		print("\n")
		print("\t------------------------------------")
		for x in self.wallet.utxoslocal:
			x.print_trans()
			print("\t------------------------------------")
		print("[END DEBUGGING RUN TRANSACTION LOCAL]")
		return
			

	def run_transaction(self, T):
		transaction_inputs = T.transaction_inputs
		transaction_outputs = T.transaction_outputs
		print("[ENTER]: run_transaction\n")
		for t_in in transaction_inputs:
			temp = self.wallet.utxos.copy()
			for t in temp:
				if t_in.transaction_id == t.transaction_id and t_in.address == t.address and t_in.amount == t.amount:
					self.wallet.utxos.remove(t)
					break
		
		for t_out in transaction_outputs:
			if (t_out.amount > 0):
				self.wallet.utxos.append(t_out)
		
		self.wallet.utxoslocal = self.wallet.utxos.copy()
		print("[EXIT]: run_transaction\n")
		return
	
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

		if T.sender_address == T.receiver_address:
			print("[Transaction]: ERROR: You can't send money to yourself")
			return False
		transaction_inputs = T.transaction_inputs

		if transaction_inputs == []:
			print("[Validation Failed]: You got no inputs bozo!")
			return False

		for t_in in transaction_inputs:
			res = False 
			# print("[Iteration Start]---------------------------------")
			for t_utxo in self.wallet.utxoslocal:
				# print("\t\t\t----------------START-----------------")
				# t_utxo.print_trans()
				# print("\t\t\t---------------------------------")
				# t_in.print_trans()
				# print("\t\t\t----------------END-----------------")
				if t_in.transaction_id == t_utxo.transaction_id and t_in.address == t_utxo.address and t_in.amount == t_utxo.amount:
					res = True
			if t_in.amount <= 0:
				res = False
			if res == False:
				print("\n")
				print("\t\t[Validation Failed]: Transaction Input didn't match UTXOs or had no money")
				print("\t\t\tTransaction that didn't match:")
				t_in.print_trans()
				print("Validation Error Message END\n")
				return False
			# print("[Iteration End]---------------------------------")
			
		return True



	def add_transaction_to_block(self):
		while(self.block_run.is_set()):
			#print(co.colored('Block previous hash: ' + self.block.previousHash, 'yellow'))
			if(len(self.block.listOfTransactions) < CAPACITY):
				if(self.transaction_pool!=[]):
					print(co.colored('Adding Transaction to Block: ' + str(self.block.previousHash),"green"))
					# Take first transaction of pool, remove it and add it to current block
					T = self.transaction_pool[0]
					self.transaction_pool.remove(T)
					if (self.validate_transaction(T)):
						self.block.add_transaction(T)
						self.run_transaction_local(T)
						print(len(self.block.listOfTransactions),' of ', CAPACITY)
						for tr in self.block.listOfTransactions:
							tr.print_trans()
					print('\naddtrans\n')
					print(co.colored(self.block.nonce,"green"))
					print(co.colored(self.block.listOfTransactions,"green"))
			else:
				self.doMine.set()
				self.mine_thread = threading.Thread(target = self.mine_block, args=[self.block])	
				self.mine_thread.start()
				self.block_run.clear()
				return
		self.block_run.clear()
		return

	def mine_block(self, B):
		b = B.copy()
		print("[Start]: Mining...")
		start = time.time()		
		while self.doMine.is_set():
			b.hash = b.myHash()
			print(co.colored(b.hash, 'yellow'))
			if self.valid_proof(b.hash):
				self.broadcast_block(b)
				self.doMine.clear()
				return
			else:
				b.nonce = random.getrandbits(32)
		duration = time.time() - start
		if(self.valid_proof(b.hash)):
			# self.create_new_block(self.block.hash)
			print("[END]: Mine Duration ->", duration)
		else:
			print("[END]: Mine was interrupted")
		return

	def broadcast_block(self,b):
		dic_blck = b.to_dict()
		print("[Broadcast]: Broadcasting ...")
		print("\tBlock: ", dic_blck)
		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip + port + '/'
			# data = json.dumps(dic)
			res = requests.post(url + 'broadcastBlock', json = dic_blck)
		print("[Broadcast]: END")
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

	def validate_block(self, B):
		print(co.colored("[ENTER]: validate_block\n", "red"))
		if not self.valid_proof(B.hash):
			print("[EXIT]: validate_block\n")
			return False
		for t in B.listOfTransactions:
			if not self.validate_transaction(t):
				print("[EXIT]: validate_block : unvalid\n")
				return False
			self.run_transaction_local(t)
		print("[EXIT]: validate_block : valid\n")
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
		print("[ENTER]: reverse_blocks_until_conflict\n")
		for b in reversed(self.chain.blocks):
			if b.hash == conflict_hash:
				break
			else:
				for t in b.listOfTransactions:
					self.reverse_transaction(t)
		print("[EXIT]: reverse_blocks_until_conflict\n")
		return

	def validate_chain(self, chain, conflict_hash):
		print("[ENTER]: validate_chain\n")
		current_hash = conflict_hash
		restore_point = self.wallet.utxoslocal.copy()
		self.wallet.utxoslocal = self.wallet.utxos.copy()
		self.reverse_blocks_until_conflict(conflict_hash)
		for b in chain:
			if not (self.validate_block(b) and b.previousHash == current_hash):
				self.wallet.utxoslocal = restore_point.copy()
				print("[EXIT]: validate_chain\n")
				return False
			current_hash = b.hash
		print("[EXIT]: validate_chain\n")
		return True


	# #concencus functions

	def valid_chain(self):
		#check for the longer chain across all nodes
		print("[ENTER]: valid_chain\n")
		chain_length = len(self.chain.blocks)
		hashes = [x.hash for x in self.chain.blocks]
		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip + port + '/'
			# data = json.dumps(dic)
			res = requests.post(url + 'broadcastvalidChain', 
		       json = {'chain_length': chain_length , 'hashes': hashes})
		print('[EXIT]: valid_chain\n')
		return


	def resolve_conflicts(self):
		# resolve correct chain
		max_length = len(self.chain.blocks)
		new_chain = None
		hashes = [x.hash for x in self.chain.blocks]
		for _, value in self.ring.items():
			ip = value[1]
			url = 'http://' + ip + port + '/'
			response = requests.get(url + 'consensus')
			if response.status_code == 200:
				length = response.json()['length']
				chain = self.to_chain(response.json())
				if length > max_length and self.validate_chain(chain):
					max_length = length
					new_chain = chain
		if new_chain:
			self.chain = new_chain
			new_hashes = [x.hash for x in self.chain.blocks]
			common_block_hash = ''
			for i in range(0, len(hashes)):
				if hashes[i] != new_hashes[i]:
					common_block_hash = hashes[i-1]
					break

				
			return True
		return False

	def to_chain(self, dict):
		chain = dict['chain']

		blocks = chain['blocks']
		capacity = chain['capacity']

		block_list = []
		for x in blocks:
			prev_hash = x['previousHash']
			ts = x['timestamp']
			nonce = x['nonce']
			transactions = x['listOfTransactions']
			
			t_list = []
			for t in transactions:
				sender_address = t['sender_address'].encode()
				receiver_address = t['receiver_address'].encode()
				amount = t['amount']
				signature = base64.b64decode(t['signature'].encode())
				transaction_inputs = [transaction.TransactionIO(r[0], bytes(r[1],'utf-8'), int(r[2])) for r in t['transaction_inputs']]
				t_list.append(transaction.Transaction(sender_address, receiver_address, amount, transaction_inputs, signature=signature))

			block_list.append(Block(prev_hash, ts, nonce, t_list))

		ret_chain = blockchain.BlockChain(capacity=capacity)
		ret_chain.blocks = block_list.copy()

		return ret_chain



	#cli commands
	def balance():
		url = 'http://' + ip + port + '/getBalance'
		response = requests.get(url)
		print('Your balance is :', response.text)
		return response
	
	def view():
		url = 'http://' + ip + port + '/view'
		response = requests.get(url)
		re = response.json()
		print('List of transaction of last block of blockchain')
		print(re['listOfTransactions'])

	def sendTransCli(id, amount):
		url = 'http://' + ip + port + '/sendTransaction?to='+str(id)+'&amount='+str(amount)
		# print(url)
		response = requests.get(url)
		if(response.status_code == 200):
			print('Transcation is send!')
		else:
			print('Transaction was not send please repeat!')

	def run_trans_from_txt(self):
		project_path = "./"
		time.sleep(5)
		if self.id != 0: requests.get("http://" + ip  + port + "/login")
		time.sleep(50)
		f = open(project_path + "5nodes/transactions{}.txt".format(self.ring[self.wallet.address.decode()][0]), "r")
		s = " "
		s = f.readline()
		while s != "":
			[r, amount] = s.split()
			rcv = r[2:]
			# if int(rcv) >= total: continue
			requests.get("http://" + ip  + port + "/sendTransaction?to=" + rcv + '&amount=' + amount)
			time.sleep(3)
			s = f.readline()