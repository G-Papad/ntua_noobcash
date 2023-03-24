import requests
from flask import Flask, jsonify, request, render_template
import json
# from flask_cors import CORS
import base64

import node
import blockchain
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

@app.route('/getBalance', methods=['GET', 'POST'])
def getBalance():
    balance = myNode.wallet.balance()
    print(balance)
    # ret = str(balance)
    return str(balance)

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
        print("Transaction added to current Block!")
        # print(myNode.wallet.utxos)
        # myNode.run_transaction_local(T)
        # for x in myNode.wallet.utxos:
        #     print(x.transaction_id, x.amount)
    else:
        print("You cant steal from me bozo! [Transaction Failed Validation]")
        
    
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
    myNode.ring = ring.copy()
    print('\n')
    print("THIS IS THE RING")
    print(ring)
    print("END RING")
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
    myNode.chain.blocks = block_list.copy()
    myNode.chain.capacity = capacity
    # print("I got the BlockChain")
    # print("My BlockChain length is: ", len(myNode.chain.blocks))
    # print("Running BlockChain from the start...")
    myNode.run_blockchain()
    prevHash = myNode.chain.blocks[len(myNode.chain.blocks)-1].hash
    myNode.create_new_block(prevHash)

    return 'ok'

@app.route('/broadcastBlock', methods=['POST'])
def receive_block():
    temp = json.loads((request.data).decode())
    prev_hash = temp['previousHash']
    ts = temp['timestamp']
    nonce = temp['nonce']
    transactions = temp['listOfTransactions']
    
    t_list = []
    for t in transactions:
        sender_address = t['sender_address'].encode()
        receiver_address = t['receiver_address'].encode()
        amount = t['amount']
        signature = base64.b64decode(t['signature'].encode())
        transaction_inputs = [transaction.TransactionIO(r[0], bytes(r[1],'utf-8'), int(r[2])) for r in t['transaction_inputs']]
        t_list.append(transaction.Transaction(sender_address, receiver_address, amount, transaction_inputs, signature=signature))
    newBlock = block.Block(prev_hash, ts, nonce, t_list)
    if(newBlock.previousHash == myNode.block.previousHash):
        restore_point = myNode.wallet.utxoslocal.copy()
        myNode.wallet.utxoslocal = myNode.wallet.utxos.copy()    
        if myNode.validate_block(newBlock):        
            # newBlock continues myNode chain
            myNode.chain.add_block(block.Block(prev_hash, ts, nonce, t_list))
            myNode.block = newBlock
            myNode.run_block()
            myNode.create_new_block(myNode.chain.blocks[len(myNode.chain.blocks)-1].hash)
        else:
            myNode.wallet.utxoslocal = restore_point.copy()
    else:
        myNode.valid_chain()
        #newCode
    return 'blook'

@app.route('/broadcastvalidChain', methods=['POST'])
def send_chain():
    temp = json.loads((request.data).decode())
    chain_length = temp['chain_length']
    hashes = temp['hashes']
    conflict_hash=''
    ip=request.remote_addr

    if chain_length < len(myNode.chain.blocks):
        i=0
        for b in myNode.chain.blocks:
            if  i < len(hashes) and b.hash == hashes[i]:
                i += 1
            else:
                blocks_to_send = myNode.chain.blocks[i:] 
                conflict_hash = b.hash
                break
        blockchain_to_send = blockchain.BlockChain()
        blockchain_to_send.blocks = blocks_to_send.copy()
        url = 'http://' + ip + ':5000/'
        requests.post(url+'receiveValidChain', 
                      json={'length' : len(myNode.chain.blocks),
            'chain' : blockchain_to_send.to_dict(),
            'conflict_hash' : conflict_hash}) 
    return 'send chain'

@app.route('/receiveValidChain', methods=['POST'])
def receive_chain():
    temp = json.loads((request.data).decode())
    chain = temp['chain']
    length = temp['length']
    conflict_hash = temp['conflict_hash']
    
    blocks = chain['blocks']
    
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

    if(len(myNode.chain.blocks) < length):
        if myNode.validate_chain(block_list, conflict_hash):
            #update our blockchain
            temp_list = reversed(myNode.chain.blocks)
            for b in temp_list:
                if b.hash != conflict_hash:
                    myNode.chain.blocks.remove(b)
                else:
                    break
            for b in block_list:
                myNode.chain.add_block(b)
            myNode.wallet.utxos = myNode.wallet.utxoslocal.copy()
            myNode.create_new_block(block_list[len(block_list)-1].hash)

    return "receive chain"

@app.route('/sendTrans', methods=['GET'])
def send():
    for keys,v in myNode.ring.items():
        if keys != myNode.wallet.public_key.decode():
            receiver=keys
    myNode.create_transaction(receiver=receiver.encode(), amount=50)
    return "sendTrans page"

@app.route('/sendTransaction', methods=['GET', 'POST'])
def make_transaction():
    args = request.args
    receiver_id = int(args.get('to'))
    amount = int(args.get('amount'))
    receiver = None
    for pk,value in myNode.ring.items():
        if value[0] == receiver_id:
            receiver = pk
    if(receiver == None):
        print('Receiver not found!')
    else:
        myNode.create_transaction(receiver.encode(), amount)
    return 'sendTransactionPage'

@app.route('/view', methods=['GET'])
def view():
    last_block = myNode.chain.blocks[len(myNode.chain.blocks)-1]
    list_of_trans = last_block.listOfTransactions
    for x in list_of_trans:
        x.print_trans()

    return jsonify(last_block.to_dict())

@app.route('/help', methods=['GET'])
def help():
    help_str='''
    HELP\n
    Available commands:\n
    t <recipient_address> <amount> \n
    \t--New transaction: send to recipient_address wallet the amount amount of NBC coins to get from wallet sender_address. It will call create_transaction function in the backend that will implements the above function.\n
    view\n
    \t--View last transactions: print the transactions contained in the last validated block of noobcash blockchain.\n
    balance\n
    \t--Show balance: print the balance of the wallet.\n
    help\n
    '''
    print(help_str)
    return help_str

@app.route('/printBlockchain', methods=['GET'])
def print_blockchain():
    str_chain = myNode.chain.to_dict()
    return str_chain

@app.route('/getAllBalance', methods=['GET'])
def print_all_balance():
    dic = {}
    for address in myNode.ring.keys():
        dic[address] = sum([x.amount for x in myNode.wallet.utxos if x.address == address])

    return dic

if __name__ == '__main__':
    from argparse import ArgumentParser  

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    myNode = node.Node()
    # print(myNode.wallet.public_key)

    # myBlock = myNode.create_new_block()
    
    app.run(host='192.168.1.9', port=port)
    