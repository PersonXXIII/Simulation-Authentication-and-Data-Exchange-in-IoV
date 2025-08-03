import os
import json

def generate_auth_node_twins(json_directory):
    # Static values for fields that are constant
    location = "1234 4321"
    bc_target = "dtmi:SimulationForIoV:Cloud;1"
    vehicle_target = "dtmi:SimulationForIoV:Vehicle;1"
    pedestrian_device_target = "dtmi:SimulationForIoV:PedestrianDevice;1"
    model = "dtmi:SimulationForIoV:AuthN;1"

    # List of JSON files in the directory
    json_files = [f for f in os.listdir(json_directory) if f.endswith('.json')]

    twin_ids = []  # List to store the Digital Twin IDs
    payloads = {}   # Dictionary to store payloads for quick lookup

    # Loop through each file, extract the necessary fields and create the payload
    for i, json_file in enumerate(json_files, start=1):
        with open(os.path.join(json_directory, json_file), 'r') as file:
            data = json.load(file)
            
            # Extract the necessary fields
            auth_node_id = data.get("username", "")
            auth_node_ph = data.get("password_hash", "")
            auth_node_type = data.get("entity_type", "")
            
            # Create the payload for the Digital Twin
            payload = {
                "$dtId": f"AuthNode_{auth_node_id}",
                "$model": model,
                "AuthNode_ID": auth_node_id,
                "AuthNode_PH": auth_node_ph,
                "AuthNode_Type": auth_node_type,
                "Location": location,
                "VerifiesWithBC1": {
                    "$target": bc_target
                },
                "StoresInBC2": {
                    "$target": bc_target
                },
                "StoresInBC3": {
                    "$target": bc_target
                },
                "AuthRequestResponse": {
                    "$target": vehicle_target
                },
                "VerifyDevice": {
                    "$target": pedestrian_device_target
                }
            }
            
            # Store the payload in the dictionary using the Digital Twin ID as key
            twin_id = f"AuthNode_{auth_node_id}"
            payloads[twin_id] = payload
            
            # Append the twin ID to the list
            twin_ids.append(twin_id)
            
            # Print the payload for verification (optional)
            # print(f"Payload for {twin_id}: {json.dumps(payload, indent=4)}")
            
    return twin_ids, payloads


def fetch_digital_twin_by_id(twin_id, payloads):
    """
    Fetch the Digital Twin data by its ID.
    
    :param twin_id: The ID of the Digital Twin to fetch.
    :param payloads: The dictionary containing all the payloads.
    :return: The payload corresponding to the given twin_id or None if not found.
    """
    return payloads.get(twin_id, None)


