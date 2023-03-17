import block
import wallet
import transaction

log = []

class Node:
	def __init__(self):
		self.NBC=100;
		##set

		#self.chain
		#self.current_id_count
		#self.NBCs
		self.wallet = self.create_wallet()

		#slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 


	def create_new_block():
		return

	def create_wallet(self):
		return wallet.wallet()

	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		return

	def create_transaction(self, receiver, amount):
		#remember to broadcast it
		s = 0
		me = self
		transactionInputs = []
		for t in self.wallet.utxos:
			if s >= amount: break
			if t.address == me.wallet.address: 
				transactionInputs.append(t)
				s += t.amount
		self.broadcast_transaction(transaction.Transaction(self.wallet.public_key, receiver, amount, self.wallet.private_key, transactionInputs))


	def broadcast_transaction(self,x):
		log.append(x)

	def receive(self):
		newT = log[0]
		# validate
		for x in newT.transaction_inputs:
			self.wallet.utxos.remove(x)
		for x in newT.transaction_outputs:
			self.wallet.utxos.append(x)
	# def validate_transaction():
	# 	#use of signature and NBCs balance


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



