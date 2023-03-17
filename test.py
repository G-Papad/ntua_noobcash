import transaction
import node
import wallet

n1 = node.Node()
n2 = node.Node()

n1.wallet.utxos.append(transaction.TransactionIO(5, n1.wallet.public_key, 100))
n2.wallet.utxos.append(transaction.TransactionIO(5, n1.wallet.public_key, 100))

n1.create_transaction(n2.wallet.public_key, 50)
n2.receive()
print(n1.wallet.balance())
print("\n")
print(n2.wallet.balance())