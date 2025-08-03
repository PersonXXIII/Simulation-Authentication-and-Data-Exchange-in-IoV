# Get data from BC1 using Proof.
from web3 import Web3
from web3.exceptions import Web3Exception
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
abi = os.path.join(base_dir, "../../build/contracts/BC1.json")


class VehicleRegistry:
    def __init__(self, proof, url, contract_address, abi_path=abi, account_index=0):
        self.proof = proof

        # Connect to the Ethereum network
        self.web3 = Web3(Web3.HTTPProvider(url))
        if not self.web3.is_connected():
            raise ConnectionError("Failed to connect to the Ethereum network.")
        
        # Set the default account
        self.account = self.web3.eth.accounts[account_index]
        self.web3.eth.default_account = self.account
        
        # Load contract ABI
        with open(abi_path, "r") as file:
            contract_json = json.load(file)
            self.abi = contract_json["abi"]
        
        # Instantiate the contract
        self.contract = self.web3.eth.contract(address=self.web3.to_checksum_address(contract_address), abi=self.abi)
        
        # Fetch vehicle data immediately upon initialization
        self.vehicle_data = self.get_vehicle_by_proof(self.proof)
    
    def get_vehicle_by_proof(self, proof):
        try:
            # Call the contract function
            vehicle = self.contract.functions.getVehicle(proof).call()
            Data = {
                "brand": vehicle[0],
                "model": vehicle[1],
                "year": vehicle[2],
                "vin": vehicle[3],
                "hashed_vin": vehicle[4],
                "encrypted_vin": vehicle[5],
                "public_key": vehicle[6],
                "private_key": vehicle[7],
                "ta_signature": vehicle[8]
            }
            if Data:
                return True, Data
            else:
                return False, None

        except Exception as e:
            # print(f"An unexpected error occurred: {str(e)}")
            return False, None
    
    def get_response(self):
        return self.vehicle_data

