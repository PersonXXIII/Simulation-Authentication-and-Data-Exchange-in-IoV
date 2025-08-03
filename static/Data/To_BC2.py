from web3 import Web3
import json
import os

def add_auth_log(url, contract_address, temp_vehicle_ID, proof, outcome, VIN, hashed_VIN, sessionKey, date, node):
    
    # Connect to the Ethereum network (Ganache)
    web3 = Web3(Web3.HTTPProvider(url))
    
    # Use the first unlocked account from Ganache
    account = web3.eth.accounts[0]
    web3.eth.default_account = account

    # Load contract ABI
    with open(os.path.join("build/contracts/BC2.json"), "r") as file:
        contract_json = json.load(file)
        abi = contract_json["abi"]

    # Connect to contract
    contract = web3.eth.contract(address = contract_address, abi=abi)
    
    # Send transaction using unlocked account (no manual signing)
    tx_hash = contract.functions.addAuthLog(
        temp_vehicle_ID,
        proof,
        outcome,
        VIN,
        hashed_VIN,
        sessionKey,
        date,
        node
    ).transact({
        'from': account,
        'gas': 2000000,
        'gasPrice': web3.to_wei('20', 'gwei')
    })

    # Wait for receipt
    txn_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return txn_receipt
