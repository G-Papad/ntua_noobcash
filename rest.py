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
    print('sig', sig)
    print('sa', sa)
    T = transaction.Transaction(sa, ra, amount, [])
    b = T.verify_signature(sig)
    print(b)
    return temp

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)