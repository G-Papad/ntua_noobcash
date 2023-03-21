import transaction
import node
import wallet
import requests

# n1 = node.Node()
# n2 = node.Node()
# ring = n1.register_node_to_ring(n2.wallet.address, '127.0.0.1:5000')
# n2.ring = {}
# for x in ring:
#     n2.ring[x] = ring[x].copy()

# # n1.wallet.utxos.append(transaction.TransactionIO(5, n1.wallet.public_key, 200))
# # n2.wallet.utxos.append(transaction.TransactionIO(5, n1.wallet.public_key, 200))

# n1.create_transaction(n2.wallet.public_key, 100)
# n1.receive()
# n2.receive()
# node.log.pop()

# n1.create_transaction(n2.wallet.public_key, 30)
# n1.receive()
# n2.receive()
# print(n1.wallet.balance())
# print("\n")
# print(n2.wallet.balance())

# for x in n1.ring:
#     print(n2.ring[x])

master_url='http://192.168.1.4:5000/register'
pk = b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDOuTjiNxAN9IWzZ5wETmMFie8R\nVla2HaQ34Of7R30ck97fvtIVnqcmtKO1ZKKn66LdDWn0qsPbEC21leyOaGWOLmZz\nfU/AmJiJv+EJ5cJU4tIz9s30dkXmRPrBvTgxUMHPsP4t8XCB7TuVAg8vWp1ysyv5\nRF63fWPel8Pjiqqu+QIDAQAB\n-----END PUBLIC KEY-----'
requests.post(master_url, json={'public_key': pk.decode()})