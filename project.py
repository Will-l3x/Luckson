import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain =[]
        self.nodes = set()

        #create the genesis block to start the blockchain
        self.new_block(previous_hash='1',proof=100)

    def register_node(self,address, nodename):
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """



        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            #Accepts a url without the scheme like '192.168.0.1
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    
    def valid_chain(self,chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-------------\n")
            #check that the hash of the block is correct

            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False
            

            #check that the proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False
            
            last_block = block
            current_index +=1
        
        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),

        }

        #reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block
    
    def new_transaction_desk(self, PatientID, PatientName, PatientSurname, CovidStatus, Dateofcertificate, Temperature):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'PatientID': PatientID,
            'PatientName': PatientName,
            'PatientSurname': PatientSurname,
            'CovidStatus': CovidStatus,
            'Temperature':Temperature,
            'DateofCertificate': Dateofcertificate

        })

        return self.last_block['index'] +  1
    
    def new_transaction_admission(self,PatientID, NextofKin, Gender, Age, DOB, IDNumber, MaritalStatus, EmailAddress, MedicalAid, MedicalAidNumber, ConsultationFee, TestsFee):

        self.current_transactions.append({
            'PatientID': PatientID,
            'NextofKin': NextofKin,
            'Gender': Gender,
            'Age': Age,
            'DOB': DOB,
            'IDNumber': IDNumber,
            'MaritalStatus': MaritalStatus,
            'EmailAddress': EmailAddress,
            'MedicalAid': MedicalAid,
            'MedicalAidNumber': MedicalAidNumber,
            'ConsultationFee': ConsultationFee,
            'TestsFee': TestsFee,


        })
        return self.last_block['index'] + 1
    
    def new_transaction_Assessment(self, PatientID, Notes, Allergies, Symptoms, BP, Pulse, Temperature, Respirations, Oxygen, Weight, Height, PriorityLevel):

        self.current_transactions.append({
            'PatientID': PatientID,
            'Notes': Notes, 
            'Allergies': Allergies,
            'Symptoms': Symptoms,
            'BP': BP,
            'Pulse': Pulse,
            'Temperature': Temperature,
            'Respirations': Respirations,
            'Oxygen': Oxygen,
            'Weight': Weight,
            'Height': Height,
            'PriorityLevel': PriorityLevel,
        })
        return self.last_block['index'] + 1
    
    def new_transaction_Doctor(self, PatientID, LabNotes, Diagnosis, prescription, recommendation):

        self.current_transactions.append({
            'PatientID': PatientID,
            'LabNotes': LabNotes,
            'Diagnosis': Diagnosis,
            'Prescription': prescription,
            'recommendation': recommendation,

        })
        return self.last_block['index'] + 1
    
    def new_transaction_Lab(self, PatientID, BloodTest, Xray, UltraSound, Cultures, Lipid, Hemoglobin, urinanalysis, other):

        self.current_transactions.append({
            'PatientID': PatientID,
            'BloodTest': BloodTest,
            'Xray': Xray,
            'UltraSound': UltraSound,
            'Cultures': Cultures,
            'Lipid': Lipid,
            'Hemoglobin': Hemoglobin,
            'urinanalysis': urinanalysis,
            'other': other

        })
        return self.last_block['index'] + 1
    
    def new_transaction_Dispensary(self, PatientID, Medication):
        
        self.current_transactions.append({
            'PatientID': PatientID,
            'Medication': Medication,
        })
        return self.last_block['index'] + 1
    

    

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
            Creates a SHA-256 hash of a Block
            :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
         
        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
#Instantiate the node
app = Flask(__name__)

#generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

#Instantiate the blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction_desk(
        PatientID = 0,
        PatientSurname = node_identifier,
        PatientName = "Genesis Block",
        CovidStatus = "Genesis Block",
        Temperature = "Genesis Block",
        Dateofcertificate = "Genesis Block"
        
    ) 

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/mineadmission', methods=['GET'])
def mineAdmin():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction_admission(
        PatientID = node_identifier,
        NextofKin =  "Genesis Block",
        Gender = "Genesis Block",
        Age = "Genesis Block",
        DOB = "Genesis Block",
        IDNumber= 'IDNumber',
        MaritalStatus = 'MaritalStatus',
        EmailAddress = 'EmailAddress',
        MedicalAid = 'MedicalAid',
        MedicalAidNumber = 'MedicalAidNumber',
        ConsultationFee =  'ConsultationFee',
        TestsFee = 'TestsFee',
    
        
    ) 

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/mineassessment', methods=['GET'])
def mineAssessment():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction_Assessment(
        PatientID = node_identifier,
        Notes = 'Notes', 
        Allergies = 'Allergies',
        Symptoms = 'Symptoms',
        BP =  'BP',
        Pulse = 'Pulse',
        Temperature = 'Temperature',
        Respirations = 'Respirations',
        Oxygen = 'Oxygen',
        Weight = 'Weight',
        Height = 'Height',
        PriorityLevel= 'PriorityLevel',
        
       
    
        
    ) 

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/mineDoctor', methods =['Get'])
def mineDoc():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction_Doctor(
        PatientID = node_identifier,
        LabNotes = 'LabNotes',
        Diagnosis = 'Diagnosis',
        prescription = 'prescription',
        recommendation = 'recommendation',
        
       
    
        
    ) 

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/minelab', methods=['Get'])
def minelab():
     # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction_Lab(
        PatientID= 'PatientID',
        BloodTest = 'BloodTest',
        Xray = 'Xray',
        UltraSound= 'UltraSound',
        Cultures ='Cultures',
        Lipid = 'Lipid',
        Hemoglobin = 'Hemoglobin',
        urinanalysis = 'urinanalysis',
        other = 'other'
        
       
    
        
    ) 

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/mineDispensary', methods=['Get'])
def mineDispensary():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction_Dispensary(
        
        Medication = "Medication",
        PatientID = node_identifier,
        
        
       
    
        
    ) 

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/newdesk', methods=['POST'])
def new_transaction_newdesk():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['PatientID', 'PatientName', 'PatientSurname','CovidStatus', 'Temperature', 'DateofCertificate']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction_desk(values['PatientID'],values['PatientName'], values['PatientSurname'], values['CovidStatus'],values['Temperature'], values['DateofCertificate'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/transactions/newadmin', methods=['POST'])
def new_transactions_newadmin():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['PatientID',
                'NextofKin',
                'Gender',
                'Age',
                'DOB',
                'IDNumber',
                'MaritalStatus',
                'EmailAddress',
                'MedicalAid',
                'MedicalAidNumber',
                'ConsultationFee',
                'TestsFee' ]
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction_admission(values['PatientID'],values['NextofKin'], values['Gender'], values['Age'],values['DOB'], values['IDNumber'],values['MaritalStatus'], values['EmailAddress'],values['MedicalAid'], values['MedicalAidNumber'],values['ConsultationFee'], values['TestsFee'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201 

@app.route('/transactions/newassessment', methods=['POST'])
def new_transaction_ass():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['PatientID',
                'Notes', 
                'Allergies',
                'Symptoms',
                'BP',
                'Pulse',
                'Temperature',
                'Respirations',
                'Oxygen',
                'Weight',
                'Height',
                'PriorityLevel',]
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction_Assessment(values['PatientID'],values['Notes'], values['Allergies'], values['Symptoms'],values['BP'], values['Pulse'],values['Temperature'], values['Respirations'],values['Oxygen'], values['Weight'],values['Height'], values['PriorityLevel'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201 

@app.route('/transactions/newdoctor', methods=['POST'])
def new_transaction_doc():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['PatientID',
                'LabNotes',
                'Diagnosis',
                'Prescription',
                'recommendation',]
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction_Doctor(values['PatientID'],values['LabNotes'], values['Diagnosis'], values['Prescription'],values['recommendation'],)

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201 

@app.route('/transactions/newlab', methods=['POST'])
def new_transaction_labs():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['PatientID',
                'BloodTest',
                'Xray',
                'UltraSound',
                'Cultures',
                'Lipid',
                'Hemoglobin',
                'urinanalysis',
                'other']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction_Lab(values['PatientID'],values['BloodTest'], values['Xray'], values['UltraSound'],values['Cultures'],values['Lipid'], values['Hemoglobin'],values['urinanalysis'],values['other'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201 

@app.route('/transactions/newDisp', methods=['POST'])
def new_transaction_disp():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['PatientID',
                'Medication',]
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction_Dispensary(values['PatientID'],values['Medication'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/deskchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New node has been registered',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)

    
