import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
import jsonpickle

# create the class block to maintain the block information


class Block(object):

    def __init__(self, block_id, block_data, block_prev_hash, proof):
        self._block_id = block_id
        self._block_data = block_data
        self._block_prevHash = block_prev_hash
        self._proof = proof

    def get_block_id(self):
        return self._block_id

    def get_block_data(self):
        return self._block_data

    def get_block_prev_hash(self):
        return self._block_prevHash

    def get_block_proof(self):
        return self._proof


class Transaction(object):
    def __init__(self, sender, receiver, amount):
        self._sender = sender
        self._receiver = receiver
        self._amount = amount

    def get_sender(self):
        return self._sender

    def get_receiver(self):
        return self._receiver

    def get_amount(self):
        return self._amount


class NeedCoin:
    def __init__(self):
        self.block_chain = []  # store the list of block and block will contain transaction
        self.transaction = []  # store the list of the transaction (basically choosing from mem-pool)
        block = self.create_block(1, 0)  # genesis block is created and added but not mined yet
        self.add_new_block(block)  # added to the block-chain network
        self.node = set()

    def create_block(self, proof, prev_hash):
        block = Block(len(self.block_chain), self.transaction, prev_hash, proof)  # create new block
        return block

    def add_new_block(self, block):
        self.transaction = []  # to avoid double spending problem
        self.block_chain.append(block)

    def get_last_block(self):
        return self.block_chain[-1]  # return the last block in the chain

    def add_new_transaction(self, sender, receiver, amount):
        new_transaction = Transaction(sender, receiver, amount)
        self.transaction.append(new_transaction)
        last_block = self.get_last_block()
        if isinstance(last_block, Block):
            return last_block.get_block_id()+1
        else:
            return -1

    @staticmethod
    def get_hash_block(block):
        transaction = block.get_block_data()
        excluded_last_transaction = transaction[:len(transaction)-1]
        encoded_block = (str(block.get_block_proof())
                         + str(block.get_block_prev_hash())+str(excluded_last_transaction)).encode()
        hash_block = hashlib.sha256(encoded_block).hexdigest()
        print(hash_block)
        return hash_block

    def proof_of_work(self, prev_hash):
        regex = "0000"
        new_proof = 0
        block_hash = ""
        while True:
            if block_hash[:4] == regex:
                print(block_hash)
                return new_proof
            else:
                new_proof = new_proof+1
                encoded_data = (str(new_proof) + str(prev_hash) + str(self.transaction)).encode()
                block_hash = hashlib.sha256(encoded_data).hexdigest()

    def add_nodes(self, address):
        parse_url = urlparse(address).netloc
        self.node.add(parse_url)  # added the address in  the node list

    def replace_chain(self):
        print("calling replace chain")
        network = self.node
        max_length = len(self.block_chain)
        chain = None
        flag = False
        for node in network:
            print("calling to network")
            response = requests.get('http://'+str(node)+'/get_chain')
            print(response.json())
            if response.status_code == 200:
                remote_chain_length = response.json()["length"]
                remote_chain = response.json()["chain"]
                if remote_chain_length > max_length:
                    max_length = remote_chain_length
                    chain = remote_chain
        if flag:
            self.block_chain = chain
            return True
        else:
            return False

    @staticmethod
    def to_json(obj):
        print(obj.__dict__)
        for i in range(0, len(obj.get_block_data())):
            obj.get_block_data()[i] = obj.get_block_data()[i].__dict__

        return obj.__dict__

    @staticmethod
    def to_json_chain(obj):
        print(obj.__dict__)
        return obj.__dict__

    def convert_to_json(self):
        temp = []
        for i in self.block_chain:
            temp.append(NeedCoin.to_json_chain(i))
            print(temp)
        return temp


app = Flask(__name__)

need_coin = NeedCoin()

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = need_coin.get_last_block()
    if isinstance(previous_block, Block):
        previous_hash = need_coin.get_hash_block(previous_block)
        proof = need_coin.proof_of_work(previous_hash)
        need_coin.add_new_transaction(node_address, "Miner-B", 5)  # I am taking 10$ to mine the block
        block = need_coin.create_block(proof, previous_hash)
        need_coin.add_new_block(block)
        response = {'chain': NeedCoin.to_json(block),
                    'length': len(need_coin.block_chain)}
        return jsonify(response), 200
    else:
        response = {'message': "Failed to mine the block",
                    'length': len(need_coin.block_chain)}
        return jsonify(response), 200


# Getting the full chain on the node
@app.route('/get_chain', methods=['GET'])
def get_chain():
    print("/get chain called")
    response = {'chain': need_coin.convert_to_json(),
                'length': len(need_coin.block_chain)}
    return jsonify(response), 200


# Adding a new transaction to the block chain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    request_json = request.get_json()
    index = need_coin.add_new_transaction(request_json['sender'], request_json['receiver'], request_json['amount'])
    response = {'message': "This transaction will be added to Block:"+str(index)}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node_network():
    request_json = request.get_json()
    nodes = request_json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        need_coin.add_nodes(node)
    response = {'message': 'All the nodes are now connected. The Need coins network :',
                'Total_Nodes': list(need_coin.node)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = need_coin.replace_chain()
    print("Chain replaced flag.." + str(is_chain_replaced))
    if is_chain_replaced:
        response = {'message': 'Applied the consensus protocol to syncing the chain in  the network',
                    'new_chain': need_coin.convert_to_json()}
    else:
        response = {'message': 'Nodes are already in sync.',
                    'new_chain': need_coin.convert_to_json()}
    return jsonify(response), 200

# Running the app


app.run(host='0.0.0.0', port=5002)
