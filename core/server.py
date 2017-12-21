import json
import requests
from time import time
from urlparse import urlparse
from uuid import uuid4
from flask import Flask, jsonify, request
from blockchain.core_utils import hash, proof_of_work
from blockchain.blockchain import BlockChain
from blockchain.transaction import Transaction
from blockchain.model import Model


def validator(**kwargs):
    return True

class TestTransaction(Transaction):
    @property
    def default(self):
        return TestTransaction(
            sender="0",
            recipient=str(uuid4()).replace('-', ''),
            amount=1,
        ).value

model = Model(transation_type=type(TestTransaction), model_validator=validator)
block_chain = BlockChain(model)

'''
BlockChain server:
    INPUT:
        Mother_node (with port no)
        Self_node (with port no)
        Model
'''

app = Flask(__name__)

@app.route('/mine', methods=['GET'])
def mine():
    last_block = block_chain.last_block
    last_proof = last_block['proof']
    proof = proof_of_work(last_proof)

    txn = model.transation_type().default
    block_chain.add_transactions([txn])
    
    previous_hash = hash(last_block)
    block = block_chain.new_block(proof, previous_hash)

    response = {
        'message'       : "New block mined",
        'index'         : block['index'],
        'transactions'  : block['transactions'],
        'proof'         : block['proof'],
        'previous_hash' : block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    txn = Transaction(**values)
    index = block_chain.add_transactions([txn])
    
    response = {'message': 'Transaction will be added to block {0}'.format(index)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain'     : block_chain.chain,
        'length'    : len(block_chain.chain),
    }
    return jsonify(response), 200


# TODO: need a process to auto registor nodes
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        block_chain.register_node(node)

    response = {
        'message'       : 'New nodes have been added',
        'all_nodes'     : list(block_chain.nodes),
    }
    return jsonify(response), 201

# TODO: need a process to call consensus
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = block_chain.resolve_conflicts()

    if replaced:
        response = {
            'message'   : 'This chain was replaced',
            'new_chain' : block_chain.chain
        }
    else:
        response = {
            'message'   : 'This chain is authoritative',
            'chain'     : block_chain.chain
        }

    return jsonify(response), 200

# APP thread
app.run(host='127.0.0.1', port=5001, threaded=True)
