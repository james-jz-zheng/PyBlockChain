import hashlib
import json

# Helper functions
def hash(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def proof_of_work(last_proof):
    proof = 0
    while valid_proof(last_proof, proof) is False:
        proof += 1
    return proof

def valid_proof(last_proof, proof):
    guess = '{0}{1}'.format(last_proof, proof).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"

def valid_chain(chain):
    last_block = chain[0]
    for current_index in range(1, len(chain)):
        block = chain[current_index]
        
        if block['previous_hash'] != hash(last_block): return False
        if not valid_proof(last_block['proof'], block['proof']): return False

        last_block = block

    return True
