# import requests
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO
import json
# from flask_cors import CORS
import base64

# import block
import node
# import blockchain
import wallet
import transaction
import wallet
import block


### JUST A BASIC EXAMPLE OF A REST API WITH FLASK



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


@app.route('/broadcast', methods=['POST'])
def receive_transactions():
    temp = json.loads((request.data).decode())
    temp = json.loads(temp)
    # temp = request.data
    # print(temp)
    sig = base64.b64decode(temp['signature'].encode())
    sa = bytes(temp['sender_address'], 'utf-8')
    ra = bytes(temp['receiver_address'], 'utf-8')
    amount = temp['amount']

    transaction_inputs = [transaction.TransactionIO(r[0], bytes(r[1],'utf-8'), int(r[2])) for r in temp['transaction_inputs']]
    transaction_outputs = [transaction.TransactionIO(r[0], bytes(r[1],'utf-8'), int(r[2])) for r in temp['transaction_outputs']]
    
    T = transaction.Transaction(sa, ra, amount, transaction_inputs, signature=sig)

    if (myNode.validate_transaction(T)):
        myBlock.add_transaction(T)
        print("Transcation added to current Block!")
    

    return temp

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    myNode = node.Node()

    myBlock = myNode.create_new_block()
    

    app.run(host='127.0.0.1', port=port)