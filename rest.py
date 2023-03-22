import requests
from flask import Flask, jsonify, request, render_template
import json
# from flask_cors import CORS
import base64

import node
# import blockchain
import wallet
import transaction
import wallet
import block


### JUST A BASIC EXAMPLE OF A REST API WITH FLASK


master_url='http://192.168.1.4:5000'

app = Flask(__name__)
# CORS(app)
# blockchain = Blockchain()


#.......................................................................................



# get all transactions in the blockchain

@app.route('/', methods=['GET'])
def get_transactions():
    return "hello world"
#     transactions = blockchain.transactions

#     response = {'transactions': transactions}
#     return jsonify(response), 200


@app.route('/broadcastTransaction', methods=['POST'])
def receive_transactions():
    temp = json.loads((request.data).decode())
    # temp = json.loads(temp)
    # temp = request.data
    # print(temp)
    sig = base64.b64decode(temp['signature'].encode())
    sender_adsress = bytes(temp['sender_address'], 'utf-8')
    receiver_address = bytes(temp['receiver_address'], 'utf-8')
    amount = temp['amount']

    transaction_inputs = [transaction.TransactionIO(r[0], bytes(r[1],'utf-8'), int(r[2])) for r in temp['transaction_inputs']]
    # transaction_outputs = [transaction.TransactionIO(r[0], bytes(r[1],'utf-8'), int(r[2])) for r in temp['transaction_outputs']]
    
    T = transaction.Transaction(sender_adsress, receiver_address, amount, transaction_inputs, signature=sig)
    # T.print_trans()
    # print(transaction_inputs)
    if (myNode.validate_transaction(T)):
        myNode.add_transaction_to_block(T)
        print("Transcation added to current Block!")
        print(myNode.wallet.utxos)
        myNode.run_transaction(T)
        for x in myNode.wallet.utxos:
            print(x.transaction_id, x.amount)
    else:
        print("You cant steal from me bozo!")
        
    
    return temp

@app.route('/register', methods=['POST'])
def registerNode():
    temp = json.loads((request.data).decode())

    # public_key = bytes(temp['public_key'], 'utf-8')
    public_key = temp['public_key']
    ip=request.remote_addr
    # print(ip)
    myNode.register_node_to_ring(public_key,ip)
    return '1'

@app.route('/registerFail', methods=['POST'])
def renew_pk():
    myNode.wallet = myNode.create_wallet()
    requests.post(master_url, json={'public_key': myNode.wallet.public_key.decode()})

    return '1'


@app.route('/login', methods=['GET'])
def login():
    master = master_url + '/register'
    requests.post(master, json={'public_key': myNode.wallet.public_key.decode()})
    return "Login Page"


@app.route('/broadcastNewNode', methods=['POST'])
def addNode():
    temp = json.loads((request.data).decode())

    ring = temp['ring']
    myNode.ring = ring
    
    for pk, value in ring.items():
        if(myNode.wallet.address == pk):
            myNode.id = value[0]
    # print(ring)
    return 'broadcast'

@app.route('/broadcastBlockChain', methods=['POST'])
def receiveBlockChain():
    temp = json.loads((request.data).decode())

    blocks = temp['blocks']
    capacity = temp['capacity']
    
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

        block_list.append(block.Block(prev_hash, ts, nonce, t_list))
    myNode.chain.blocks = block_list
    myNode.chain.capacity = capacity
    print("I got the BlockChain")
    print("My BlockChain length is: ", len(myNode.chain.blocks))
    print("Running BlockChain from the start...")
    myNode.run_blockchain()

    return 'ok'

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    myNode = node.Node()
    # print(myNode.wallet.public_key)

    # myBlock = myNode.create_new_block()
    myNode.create_new_block()
    
    app.run(host='192.168.1.9', port=port)
    