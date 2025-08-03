from web3 import Web3
import json
import pandas as pd
import time
import sys
import os

# Connect to the Ethereum network (e.g., Ganache)
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Check connection
if web3.is_connected():
    print("Successfully connected to the Ethereum network!")
else:
    raise ConnectionError("Failed to connect to the Ethereum network. Check your RPC URL.")

# Set default account
web3.eth.default_account = web3.eth.accounts[0]

def BC_One(BC_One_JsonPath):

    # Load contract ABI and bytecode
    with open(BC_One_JsonPath, "r") as file:
        contract_json = json.load(file)
        abi = contract_json["abi"]
        bytecode = contract_json["bytecode"]

    # Deploy contract
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Example with constructor parameters if needed:
    tx_hash = contract.constructor().transact()

    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    BC_One_AddData(tx_receipt.contractAddress, BC_One_JsonPath)
    
    return tx_receipt.contractAddress

def BC_Two(BC_Two_JsonPath):

    # Load ABI and Bytecode
    with open(BC_Two_JsonPath, "r") as file:
        contract_json = json.load(file)
        abi = contract_json["abi"]
        bytecode = contract_json["bytecode"]

    # Deploy the contract
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = contract.constructor().transact()
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_receipt.contractAddress

def BC_Three(BC_Three_JsonPath):

    # Load contract ABI and bytecode
    with open(BC_Three_JsonPath, "r") as file:
        contract_json = json.load(file)
        abi = contract_json["abi"]
        bytecode = contract_json["bytecode"]

    # Deploy contract
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = contract.constructor().transact()
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_receipt.contractAddress

def BC_One_AddData(Contract_Address, BC_One_JsonPath):

    with open(BC_One_JsonPath, "r") as file:
        contract_json = json.load(file)
        abi = contract_json["abi"]

    contract = web3.eth.contract(address=Contract_Address, abi=abi)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Directory to store the generated credentials
    CSV_DIR = os.path.join(base_dir, "Final.csv")
    df = pd.read_csv(CSV_DIR)
    ta_signature = "TA-0023"
    total = len(df)

    if total == 0:
        print("CSV is empty.")
        return

    print("\nStarting data upload:\n")
    bar_width = 40

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        try:
            contract.functions.addVehicle(
                row['Brand'],
                row['Model'],
                row['Year'],
                row['VIN'],
                row['Hashed VIN'],
                row['Encrypted VIN'],
                row['Public Key'],
                row['Private Key'],
                ta_signature,
                row['Proof']
            ).transact({'gas': 5000000})
        except Exception as e:
            pass


        # Progress bar display
        percent = i / total
        filled = int(bar_width * percent)
        bar = '█' * filled + '-' * (bar_width - filled)
        sys.stdout.write(f'\rProgress: |{bar}| {int(percent * 100)}% ({i} of {total})')
        sys.stdout.flush()

    print("\n\nDone Adding Cars Data")

