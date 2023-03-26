import block
import base64
import transaction


class BlockChain:

    def __init__(self, capacity=1):
        self.blocks = []
        self.capacity = capacity
        # self.mining_difficulty = 

    def add_block(self, block):
        self.blocks.append(block)
        return
    
    def to_dict(self):
        blockchain = {
            'blocks' : [x.to_dict() for x in self.blocks],
            'capacity' : self.capacity
        }
        return blockchain
    