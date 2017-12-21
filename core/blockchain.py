
import requests
from time import time
from urlparse import urlparse
from blockchain.core_utils import hash, valid_chain


class BlockChain:
    def __init__(self, model):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.new_block(previous_hash='1', proof=100)
        self.model = model

    def register_node(self, address):
        self.nodes.add(urlparse(address).path)

    def resolve_conflicts(self):
        neighbours, new_chain, max_length = self.nodes, None, len(self.chain)

        for node in neighbours:
            response = requests.get('http://{0}/chain'.format(node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Validate and get the longer chain
                if length > max_length and valid_chain(chain) and self.model.model_validator(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        block = {
            'index'         : len(self.chain) + 1,
            'timestamp'     : time(),
            'transactions'  : self.current_transactions,
            'proof'         : proof,
            'previous_hash' : previous_hash or hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def add_transactions(self, transactions):
        self.current_transactions.extend([t.value for t in transactions])
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]
