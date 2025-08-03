from web3 import Web3
import json
import os


def add_data(url, contract_address, node_id, comm_type, session_key, encryption_algo, processing_latency, date, time, v_temp_id, v_vin, r_type, r_temp_id, r_id, latitude, longitude, altitude, speed, direction, alerts, other_data, communication_mode):
    
    # Connect to local Ethereum node (e.g., Ganache or a custom node)
    w3 = Web3(Web3.HTTPProvider(url))  # Replace with your own node if using a different network

    # Check if connected to Ethereum network
    if not w3.is_connected():
        print("Failed to connect to the Ethereum network.")
        exit()

    # Contract ABI and Address (from Truffle deployment)
    with open(os.path.join("build/contracts/BC3.json"), "r") as file:
        contract_data = json.load(file)  # Use 'file' instead of 'f'

    abi = contract_data['abi']

    # Instantiate the contract
    contract = w3.eth.contract(address = contract_address, abi=abi)

    account_address = w3.eth.accounts[0]

    
    node_id = str(node_id)
    comm_type = str(comm_type)
    session_key = str(session_key)
    encryption_algo = str(encryption_algo)
    processing_latency = str(processing_latency)
    date = str(date)
    time = str(time)
    v_temp_id = str(v_temp_id)
    v_vin = str(v_vin)
    r_type = str(r_type)
    r_temp_id = str(r_temp_id)
    r_id = str(r_id)
    latitude = str(latitude)
    longitude = str(longitude)
    altitude = str(altitude)
    speed = str(speed)
    direction = str(direction)
    alerts = str(alerts)
    other_data = str(other_data)
    communication_mode = str(communication_mode)

    tx_hash = contract.functions.storeSession(
        node_id,
        comm_type,
        session_key,
        encryption_algo,
        processing_latency,
        date,
        time,
        v_temp_id,
        v_vin,
        r_type,
        r_temp_id,
        r_id,
        latitude,
        longitude,
        altitude,
        speed,
        direction,
        alerts,
        other_data,
        communication_mode
    ).transact({
        'from': account_address,   # Your Ganache unlocked account
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

