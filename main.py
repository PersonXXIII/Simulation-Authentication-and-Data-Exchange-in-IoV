import xml.etree.ElementTree as ET
from datetime import datetime
import traci
import os
import sys
import random
import math
import time
import json
import csv
import re

# Add the path to the folder containing the other scripts
sys.path.append(os.path.join(os.getcwd(), 'static', 'Data'))

from generate_auth_n import main_generate
from generate_V_twins import generate_twins_from_csv
from Generate_Proof import GenerateProof
from fetch_twin_data import TwinManager
from V_Data import VehicleRegistry
from generate_temp_V_ID_SessionKey import generate_session_key, generate_temp_vehicle_id
from To_BC2 import add_auth_log
from generate_Authn_twins import generate_auth_node_twins, fetch_digital_twin_by_id
from To_BC3 import add_data
from BC import BC_One, BC_Two, BC_Three

tmanager = TwinManager()



# Setting Paths
AUTH_Ns = r"static/Data/Auth_N_Credentials"
SUMO_CONFIG = r"SUMO_Network/sumo.sumocfg"
SUMO_ROUTE = r"SUMO_Network/sumo.rou.xml"
SUMO_NET = r"SUMO_Network/sumo.net.xml"
SUMO_ADDITIONAL = r"SUMO_Network/sumo.add.xml"
AUTH_Ns_JSON_DIR = r"static/Data/Auth_N_Credentials"
COLLECTED_DATA_CSV = r"Results/Collected_Data/vehicle_auth_data.csv"
COLLECTED_EXCHANGED_DATA_CSV = r"Results/Collected_Data/vehicle_exchanged_data.csv"
BAD_TWINS_FILE = r"static/Data/bad_twin_log.txt"

# Defining Global Variables
NUM_VEHICLE = 100
NUM_PED = 100

NUM_AUTH_Ns = 2
ROUTES = []
PED_ROUTES = []
BI_ROUTES = []
NODES = []
TWINS = []
VEHICLE_STATUS = {}
AUTHENTICATED_Vs = []
AUTHENTICATED_TEMP_SK_Vs = {}
AUTHENTICATED_Ps = []
VEHICLE_DATA = {}
TARGET_DISTANCE = 10
CSV_COLUMNS = ["Vehicle ID", 
               "Model", "VIN", "Public Key", "Private Key", 
               "Generated Proof", "Hashed VIN", 
               "Node", "Type", "Reason", "Temp ID", "Session Key",
               "Payload Size", "Latency", "Reliability", "Energy Efficiency", "Bandwidth Utilized",
               "Outcome", "Date", "Time" ]

CSV_COLUMNS_EX = ["Node ID", "Communication Type", "Session Key", "Algorithm", "Processing Latency", "Date", "Time", 
                  "Primary Vehicle Temp ID", "Primary Vehicle VIN", 
                  "Receiver Type", "Receiver Temp ID", "Receiver ID", "Latitude", "Longitude", "Altitude", "Speed", "Direction", "Alerts", 
                  "Other Data", "Communication Mode"]

AUTH_N_TWINS = []
STATIC_PoI_IDs = []
AUTH_N_to_PoI = {}
AUTH_N_DATA = {}
TA_AUTH_Ns_DATA = {}
AUTH_Ns_STATUS = False
AUTH_N_to_V = {}
PED_STATUS = {}
INFO_PoI = "Info"
READY_TO_EXCHANGE = False
V_ALERTS = [
    "Vehicle approaching too fast",
    "Unexpected pedestrian detected",
    "Low fuel warning",
    "Obstacle detected on the road",
    "Vehicle in dangerous proximity",
    "Unusual behavior detected",
    "Battery low warning",
    "Maintenance required",
    "Route deviation detected",
    "System malfunction alert"]

PED_ALERTS = [
    "Crossing Alert",
    "Jaywalking Alert",
    "Slow Movement Alert",
    "Running Alert", 
    "Distracted Pedestrian Alert",
    "Crowd Alert",
    "Child Alert",
    "Low Visibility Alert",
    "Unusual Behavior Alert", 
    "Emergency Vehicle Bypass Alert", 
    "Traffic Signal Violation",
    "Blocked Sidewalk Alert", 
    "Slippery Road Alert",
    "Accident Alert", 
    "Streetlight Malfunction Alert", 
    "Crowded Area Alert"
]
ALGORITHMS = [
    "AES-256-GCM",  # Strong symmetric encryption with authentication
    "ChaCha20-Poly1305",  # Secure alternative to AES, great for mobile/IoT
    "RSA-4096",  # Strong asymmetric encryption for secure key exchange
    "ECDH (Curve25519)",  # Efficient key exchange for secure communications
]

ADDRESS_ONE = BC_One(r"build/contracts/BC1.json")
ADDRESS_TWO = BC_Two(r"build/contracts/BC2.json")
ADDRESS_THREE = BC_Three(r"build/contracts/BC3.json")

URL = "http://127.0.0.1:8545"

# Additional Functions
def set_v_route():
    """Extracts available route IDs from SUMO route file."""
    tree = ET.parse(SUMO_ROUTE)
    root = tree.getroot()
    
    for route in root.findall("route"):
        ROUTES.append(route.get("id"))
    print(ROUTES)

def set_ped_routes():
    """
    Extracts all edges that allow pedestrians from a SUMO .net.xml file.

    :param SUMO_NET: Path to the SUMO network file (.net.xml)
    :param PED_ROUTES: List to store edge IDs that allow pedestrian movement
    :return: None, appends valid pedestrian edges to PED_ROUTES
    """
    # Parse the network XML file
    tree = ET.parse(SUMO_NET)
    root = tree.getroot()

    # Loop through all edges in the network
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        
        # Skip internal junction edges (e.g., :J7_* should be excluded)
        if edge_id.startswith(":"):
            continue

        # Check if this edge has any lanes that allow pedestrians
        for lane in edge.findall("lane"):
            if "pedestrian" in lane.get("allow", ""):
                # If any lane allows pedestrians, add this edge to PED_ROUTES
                PED_ROUTES.append(edge_id)
                break  # No need to check further lanes for this edge

def getting_generated_nodes():
    """Load authentication nodes from JSON files."""
    for filename in os.listdir(AUTH_Ns_JSON_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(AUTH_Ns_JSON_DIR, filename), "r") as file:
                NODES.append(json.load(file))
    return NODES

def generate_dynamic_6g_stats():

    # Simulate factors that impact 6G performance for small payloads
    payload_size_kb =random.uniform(100, 200)
    latency = random.uniform(0.1, 0.5)  # Latency in milliseconds (dynamic range: 0.1-0.5 ms)
    reliability = random.uniform(99.999, 99.99999)  # Reliability as a percentage (99.999% to 99.99999%)
    energy_efficiency = random.uniform(15, 20)  # Energy efficiency in Mbps/W (15-20 Mbps/W)
    bandwidth_utilized = payload_size_kb / random.uniform(0.8, 1.2)  # Bandwidth in Kbps (small scale usage)

    return {
        "PayloadSize": f"{payload_size_kb} KB",
        "Latency": f"{latency:.2f} ms",
        "Reliability": f"{reliability:.7f}%",
        "EnergyEfficiency": f"{energy_efficiency:.2f} Mbps/W",
        "BandwidthUtilized": f"{bandwidth_utilized:.2f} Kbps"
    }

def check_vehicle_alteration(veh_id):

    # Open the file and read its content
    try:
        with open(BAD_TWINS_FILE, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return False, f"Error: The file '{BAD_TWINS_FILE}' was not found."
    
    # Regular expression to match the alteration log pattern in the file
    regex = r"(\w+)\s+(\w+)\s+was\s+altered\.\s+Original\s+Data:\s+({.*?})\s*,\s+Altered\s+Data:\s+({.*?})"
    
    # Parse the lines and extract alterations
    for line in lines:
        match = re.search(regex, line)
        if match:
            vehicle_id = match.group(1)
            alteration_type = match.group(2)
            original_data = eval(match.group(3))  # Convert the string representation of the dictionary into a dictionary
            altered_data = eval(match.group(4))
            
            # Check if the vehicle ID matches
            if vehicle_id == veh_id:
                # Construct the reason for alteration
                reason = f"{alteration_type} was altered."
                return True, reason
    
    # If no alteration is found for the given vehicle ID
    return False, ""  # No alteration detected

def append_data_to_csv(data):
    # Append data to the existing file
    with open(COLLECTED_DATA_CSV, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)
        
def append_exchanged_data_to_csv(data):
    # Append data to the existing file
    with open(COLLECTED_EXCHANGED_DATA_CSV, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def extract_poi_ids_from_xml():
    # Parse the XML file
    tree = ET.parse(SUMO_ADDITIONAL)
    root = tree.getroot()

    # List to store the extracted POI ids
    poi_ids = []

    # Loop through each 'poi' element and extract the 'id' attribute
    for poi in root.findall(".//poi"):
        poi_id = poi.get('id')
        if poi_id:
            poi_ids.append(poi_id)
    return poi_ids

def get_direction(angle):
    if angle >= 0 and angle < 90:
        return 3 # "East"
    elif angle >= 90 and angle < 180:
        return 0 # "North"
    elif angle >= 180 and angle < 270:
        return 2 # "West"
    else:
        return 1 # "South"
    
def get_nearest_traffic_light_status(veh_id):
    vehicle_position = traci.vehicle.getPosition(veh_id)  # Get vehicle (x, y) position
    traffic_lights = traci.trafficlight.getIDList()  # Get all traffic lights

    nearest_tl = None
    min_distance = float("inf")

    for tl_id in traffic_lights:
        tl_position = traci.junction.getPosition(tl_id)  # Get traffic light position
        distance = ((vehicle_position[0] - tl_position[0]) ** 2 + 
                    (vehicle_position[1] - tl_position[1]) ** 2) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            nearest_tl = tl_id

    if nearest_tl:
        tl_status = traci.trafficlight.getRedYellowGreenState(nearest_tl)  # Get signal state
        return nearest_tl, tl_status
    else:
        return None, "No traffic light nearby"


# CSV FILE
os.makedirs(os.path.dirname(COLLECTED_DATA_CSV), exist_ok=True)

if not os.path.exists(COLLECTED_DATA_CSV):
    # If the file doesn't exist, create it and write the header row
    with open(COLLECTED_DATA_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_COLUMNS)  # Write the column headers
else:
    # If the file exists, empty the rows but keep the columns (header)
    with open(COLLECTED_DATA_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_COLUMNS)  # Write the column headers (empty the rows)

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(COLLECTED_EXCHANGED_DATA_CSV), exist_ok=True)

# Check if the file exists
if not os.path.exists(COLLECTED_EXCHANGED_DATA_CSV):
    # If the file doesn't exist, create it and write the header row
    with open(COLLECTED_EXCHANGED_DATA_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_COLUMNS_EX)  # Write the column headers
else:
    # If the file exists, empty the rows but keep the columns (header)
    with open(COLLECTED_EXCHANGED_DATA_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_COLUMNS_EX)  # Write the column headers (empty the rows)



# Load authentication nodes
print("\n\nGenerating Authentication Nodes.......")
main_generate(NUM_AUTH_Ns)
print("Auth_Ns Generated:")
getting_generated_nodes()
for index, a in enumerate(NODES):
    print(f"{index+1}. {a['entity_type']}")
time.sleep(2)

AUTH_N_TWINS, payloads = generate_auth_node_twins(AUTH_Ns_JSON_DIR)
STATIC_PoI_IDs = extract_poi_ids_from_xml()
STATIC_PoI_IDs = [poi for poi in STATIC_PoI_IDs if poi != INFO_PoI]
AUTH_N_to_PoI = dict(zip(STATIC_PoI_IDs, AUTH_N_TWINS))

for index, a in enumerate(AUTH_N_TWINS):
    auth_data = fetch_digital_twin_by_id(a, payloads)
    # Store data in AUTH_N_DATA for all POI IDs
    AUTH_N_DATA[STATIC_PoI_IDs[index]] = {
        "ID": auth_data["AuthNode_ID"],
        "Type": auth_data["AuthNode_Type"],
        "PasswordHash": auth_data["AuthNode_PH"],
        "Status": "Unknown"  # Initial status as "Unknown"
    }
    if index <=1:
        TA_AUTH_Ns_DATA[STATIC_PoI_IDs[index]] = {
            "ID": auth_data["AuthNode_ID"],
            "Type": auth_data["AuthNode_Type"],
            "PasswordHash": auth_data["AuthNode_PH"]
        }
time.sleep(2)

# Load Vehicles Twins
print("\n\nGenerating Vehicle Twins.......")
TWINS = generate_twins_from_csv(NUM_VEHICLE)
if NUM_VEHICLE == 1:
    NUM_VEHICLE = 2
else:
    NUM_VEHICLE = int(NUM_VEHICLE + (NUM_VEHICLE / 2))
print(f"{NUM_VEHICLE} Twins Generated.")

for t in TWINS:
    VEHICLE_STATUS[t] = {"status": "Unknown"}

for t in TWINS:
    twin_data = tmanager.fetch_the_twin_data_only(t)
    VEHICLE_DATA[t] = {
        "Name": twin_data.get("Name"),
        "Model": twin_data.get("Model"),
        "VIN": twin_data.get("VIN"),
        "PublicKey": twin_data.get("PublicKey"),
        "PrivateKey": twin_data.get("PrivateKey")
    }
time.sleep(2)

print("\n\nStarting SUMO Simulation.......")
time.sleep(1)

# Start SUMO
traci.start(["sumo", "-c", SUMO_CONFIG ])


# AUthenticate Nodes Authentication
if not AUTH_Ns_STATUS:
    for a in STATIC_PoI_IDs:
        if a in TA_AUTH_Ns_DATA:
            # Get the associated data from the dictionary
            auth_data = TA_AUTH_Ns_DATA[a]
            # Input password for comparison
            input_password = AUTH_N_DATA[a]["PasswordHash"]
            # Compare the input password with the stored password hash (as a string)
            if input_password == auth_data["PasswordHash"]:
                traci.poi.setColor(a, (0, 255, 0, 255))  # Green color for authenticated
                traci.poi.setType(a, f"{a} Authenticated")
            else:
                traci.poi.setColor(a, (255, 0, 0, 255))  # Red color for incorrect password
                traci.poi.setType(a, f"{a} Incorrect Password")
        else:
            traci.poi.setColor(a, (255, 0, 0, 255))  # Red color for not authorized
            traci.poi.setType(a, f"{a} Not Authorized")
    AUTH_Ns_STATUS = True

# Getting Routes
set_v_route()
set_ped_routes()

# Store mapping of vehicle to PoI
vehicle_poi_map = {}
pedestrian_route_map = {}

# Generate random spawn times for each vehicle
spawn_v_times = sorted([random.randint(0, 500) for _ in range(NUM_VEHICLE)])
spawn_v_times.sort()
next_vehicle_index = 0

# Generate random spawn times for each pedestrians
spawn_ped_times = sorted([random.randint(0, 500) for _ in range(NUM_PED)])
spawn_ped_times.sort()
next_pedestrian_index = 0
vcount = 0
pcount = 0

traci.poi.setType(INFO_PoI, f"V: {vcount} | P: {pcount}")
traci.poi.setColor(INFO_PoI, (255, 0, 0, 0))

step = 0
# Run simulation step by step
while step <= 10100:
    traci.simulationStep()
    
    traci.poi.setType(INFO_PoI, f"V: {vcount} | P: {pcount}")
    
    # --- VEHICLE GENERATION ---
    while next_vehicle_index < NUM_VEHICLE and step == spawn_v_times[next_vehicle_index]:
        veh_id = TWINS[next_vehicle_index]
        traci.vehicle.add(veh_id, random.choice(ROUTES))
        traci.vehicle.setColor(veh_id, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255))
            
        # Define PoI ID
        poi_id = f"poi_{veh_id}"

        # Get initial position
        x, y = traci.vehicle.getPosition(veh_id)

        # Add PoI above the vehicle
        traci.poi.add(poi_id, x, y + 2, (255, 0, 0, 255))

        # Set initial text for the PoI
        traci.poi.setType(poi_id, veh_id)

        # Store mapping of vehicle to PoI
        vehicle_poi_map[veh_id] = poi_id
        
        vcount += 1
        next_vehicle_index += 1

    # --- PEDESTRIAN GENERATION ---
    while next_pedestrian_index < NUM_PED and step == spawn_ped_times[next_pedestrian_index]:
        ped_id = f"ped_{next_pedestrian_index}"
        edge = random.choice(PED_ROUTES)  # Random edge from the list
        pos = random.uniform(0, 50)  # Random position (fallback length)

        # Add pedestrian
        traci.person.add(ped_id, edge, pos, float(step))  # Depart at current step
        traci.person.setColor(ped_id, (255, 0, 0, 255))  # Red color
        traci.person.appendWalkingStage(ped_id, [edge], random.choice([0, -1]))  # Random direction
        ped_status = random.choice(["Authenticated", "Not Authenticated"])
        if ped_id not in PED_STATUS:
            if ped_status == "Authenticated":
                PED_STATUS[ped_id] = {"status": ped_status}
                traci.person.setColor(ped_id, (0, 255, 0, 255))
                AUTHENTICATED_Ps.append(ped_id)
            else:
                PED_STATUS[ped_id] = {"status": ped_status}
        pcount += 1 
        next_pedestrian_index += 1
    
    # Update PoI positions dynamically
    for veh_id, poi_id in vehicle_poi_map.items():
        if veh_id in traci.vehicle.getIDList():
            x, y = traci.vehicle.getPosition(veh_id)
            traci.poi.setPosition(poi_id, x, y + 2)
            
            # Authentication Phase

            if AUTH_Ns_STATUS:
                # Generate Proof
                if VEHICLE_STATUS[veh_id].get("status") == "Unknown":
                    traci.poi.setType(poi_id, f"{veh_id} Generating Proof")
                    vin = VEHICLE_DATA[veh_id].get("VIN")
                    private_key = VEHICLE_DATA[veh_id].get("PrivateKey")
                    Hashed_VIN, proof = GenerateProof.process_proof(vin, private_key)
                    VEHICLE_STATUS[veh_id]["status"] = "Authorizing"
                
                # Validate with BC1
                elif VEHICLE_STATUS[veh_id].get("status") == "Authorizing":
                    traci.poi.setType(poi_id, f"{veh_id} Authenticating")
                
                    model = VEHICLE_DATA[veh_id].get("Model")
                    Private_Key = VEHICLE_DATA[veh_id].get("PrivateKey")
                    Public_Key = VEHICLE_DATA[veh_id].get("PublicKey")
                    vin = VEHICLE_DATA[veh_id].get("VIN")
                    private_key = VEHICLE_DATA[veh_id].get("PrivateKey")
                    Hashed_VIN, proof = GenerateProof.process_proof(vin, private_key)
                    
                    auth_n = random.choice(STATIC_PoI_IDs)
                    AUTH_N_to_V[veh_id] = {"node": auth_n}

                    result, reason = check_vehicle_alteration(veh_id)
                    type = "Bad" if result else "Good"
                    
                    current_time = datetime.now()
                    date = current_time.strftime("%Y-%m-%d")
                    
                    if AUTH_N_to_V[veh_id]["node"] in TA_AUTH_Ns_DATA:
                        vehicle_registry = VehicleRegistry(proof, URL, ADDRESS_ONE)
                        Validation, vehicle_data = vehicle_registry.get_response()
                        
                    else:
                        Validation = False
                        reason = "Invalid Authentication Node's Response."
                        
                    if Validation:
                        outcome = 'Succeed'
                        temp_vehicle_ID = generate_temp_vehicle_id()
                        sessionKey = generate_session_key()
                        node = AUTH_N_to_V[veh_id]["node"]
                        AUTHENTICATED_TEMP_SK_Vs[veh_id] = {"temp_id":temp_vehicle_ID, "sessionkey": sessionKey}
                        
                        receipt = add_auth_log(URL, ADDRESS_TWO, temp_vehicle_ID, proof, outcome, vin, Hashed_VIN, sessionKey, date, node)
                        sixg_stats = generate_dynamic_6g_stats()
                        
                        
                        row = [veh_id,
                                model, vin, Public_Key, private_key,
                                proof, Hashed_VIN,
                                node, type, reason, temp_vehicle_ID, sessionKey,
                                sixg_stats["PayloadSize"], sixg_stats["Latency"], sixg_stats["Reliability"], sixg_stats["EnergyEfficiency"], sixg_stats["BandwidthUtilized"],
                                outcome, date, current_time]
                    
                        append_data_to_csv(row)
                    
                        VEHICLE_STATUS[veh_id]["status"] = "Authorized"
                        if veh_id not in AUTHENTICATED_Vs:
                            AUTHENTICATED_Vs.append(veh_id)

                        traci.poi.setType(poi_id, f"{veh_id} Authorized")
                        traci.poi.setColor(poi_id, (0, 255, 0, 255))
                        
                        
                    elif not Validation:
                        outcome = 'Failed'
                        temp_vehicle_ID = generate_temp_vehicle_id()
                        sessionKey = generate_session_key()
                        Hashed_VIN = vin = '*'
                        node = AUTH_N_to_V[veh_id]["node"]
                        receipt = add_auth_log(URL, ADDRESS_TWO, temp_vehicle_ID, proof, outcome, vin, Hashed_VIN, sessionKey, date, node)
                        sixg_stats = generate_dynamic_6g_stats()
                        
                        row = [veh_id,
                                model, vin, Public_Key, private_key,
                                proof, Hashed_VIN,
                                node, type, reason, temp_vehicle_ID, sessionKey,
                                sixg_stats["PayloadSize"], sixg_stats["Latency"], sixg_stats["Reliability"], sixg_stats["EnergyEfficiency"], sixg_stats["BandwidthUtilized"],
                                outcome, date, current_time]
                        append_data_to_csv(row)

                        VEHICLE_STATUS[veh_id]["status"] = "Not Authorized"
                        traci.poi.setType(poi_id, f"{veh_id} Not Authorized")

                    READY_TO_EXCHANGE = True
                    
                    # Data Exchange Phase
                    if veh_id in AUTHENTICATED_Vs:
                        primary_v_vin = VEHICLE_DATA[veh_id]["VIN"]
                        p_v_temp_id = AUTHENTICATED_TEMP_SK_Vs[veh_id]["temp_id"]
                        p_v_sessionkey = AUTHENTICATED_TEMP_SK_Vs[veh_id]["sessionkey"]
                        node_id = AUTH_N_to_V[veh_id]
                        current_date = current_time.strftime("%Y-%m-%d")
                        communication = "6G"
                        algo = random.choice(ALGORITHMS)
                        
                        # For V2I
                        weather_temp = random.randrange(-10, 40)
                        w_list = ["Sunny", "Cloudy", "Rainy"]
                        weather_status = random.choice(w_list)
                        tl_id, tl_status = get_nearest_traffic_light_status(veh_id)
                        other_data = [f"Next Traffic light Status is {tl_status}.",
                                      f"Weather is {weather_status} and Temp is {weather_temp}."]
                        
                        # For V2V
                        for v in AUTHENTICATED_Vs:
                            if v != veh_id and v in traci.vehicle.getIDList():
                                i = 0
                                while i <= random.randrange(5, 20):
                                    current_time = datetime.now()
                                    communication_type = "V2V"
                                    type = "Vehicle"
                                    secondary_v_vin = VEHICLE_DATA[v]["VIN"]
                                    s_v_temp_id = AUTHENTICATED_TEMP_SK_Vs[v]["temp_id"]
                                    s_v_x, s_v_y = traci.vehicle.getPosition(v)
                                    latitude = s_v_x
                                    longitude = s_v_y
                                    altitude = random.randrange(999,1499)
                                    s_v_angle = traci.vehicle.getAngle(v)
                                    s_direction = get_direction(s_v_angle)
                                    s_speed = traci.vehicle.getSpeed(v)
                                    s_alerts = random.sample(V_ALERTS, random.randrange(1,3))
                                    sixg_stats = generate_dynamic_6g_stats()
                                    processing_latency = sixg_stats["Latency"]
                                    row = [node_id, type, p_v_sessionkey, algo, processing_latency, current_date, current_time, 
                                                      p_v_temp_id, primary_v_vin, 
                                                      type, s_v_temp_id, secondary_v_vin, latitude, longitude, altitude, s_speed, s_direction, s_alerts, 
                                                      other_data, communication]
                                    append_exchanged_data_to_csv(row)
                                    add_data(URL, ADDRESS_THREE, node_id, communication_type, p_v_sessionkey, algo, processing_latency, current_date, current_time, p_v_temp_id, primary_v_vin, type, s_v_temp_id, secondary_v_vin, latitude, longitude, altitude, s_speed, s_direction, s_alerts, other_data, communication)
                                    i += 1
                                
                        # For V2P
                        for p in AUTHENTICATED_Ps:
                            if p in traci.person.getIDList():
                                j = 0
                                while j <= random.randrange(5, 20):
                                    current_time = datetime.now()
                                    communication_type = "V2P"
                                    type = "Pedestrian"
                                    p_id = p
                                    p_temp_id = f"p_temp_{random.randrange(999, 1499)}"
                                    p_x, p_y = traci.person.getPosition(p)
                                    latitude = p_x
                                    longitude = p_y
                                    altitude = random.randrange(999,1499)
                                    p_angle = traci.person.getAngle(p)
                                    p_direction = get_direction(p_angle)
                                    p_speed = traci.person.getSpeed(p)
                                    p_alerts = random.sample(PED_ALERTS, random.randrange(1,3))
                                    sixg_stats = generate_dynamic_6g_stats()
                                    processing_latency = sixg_stats["Latency"]
                                
                                    row = [node_id, type, p_v_sessionkey, algo, processing_latency, current_date, current_time, 
                                                      p_v_temp_id, primary_v_vin, 
                                                      type, p_temp_id, p_id, latitude, longitude, altitude, p_speed, p_direction, p_alerts, 
                                                      other_data, communication]
                                    append_exchanged_data_to_csv(row)
                                    add_data(URL, ADDRESS_THREE, node_id, communication_type, p_v_sessionkey, algo, processing_latency, current_date, current_time, p_v_temp_id, primary_v_vin, type, p_temp_id, p_id, latitude, longitude, altitude, p_speed, p_direction, p_alerts, other_data, communication)
                                    j += 1
    step += 1
    time.sleep(0.01)

# Close SUMO
traci.close()
print("SUMO simulation finished.")
