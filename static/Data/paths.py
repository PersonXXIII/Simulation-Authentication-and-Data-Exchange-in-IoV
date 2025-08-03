from pathlib import Path

# Base directory of the current file (e.g., paths.py)
BASE_DIR = Path(__file__).resolve().parent

# === Static Data Paths ===
AUTH_Ns = BASE_DIR / "static" / "Data" / "Auth_N_Credentials"
AUTH_Ns_JSON_DIR = AUTH_Ns  # Just an alias, no re-joining BASE_DIR again
BAD_TWINS_FILE = BASE_DIR / "static" / "Data" / "bad_twin_log.txt"
FINAL_V_DATA = BASE_DIR / "static" / "Data" / "Final.csv"

# === SUMO Configuration ===
SUMO_DIR = BASE_DIR / "SUMO_Network"
SUMO_CONFIG = SUMO_DIR / "sumo.sumocfg"
SUMO_ROUTE = SUMO_DIR / "sumo.rou.xml"
SUMO_NET = SUMO_DIR / "sumo.net.xml"
SUMO_ADDITIONAL = SUMO_DIR / "sumo.add.xml"

# === Results Output ===
RESULTS_DIR = BASE_DIR / "Results" / "Collected_Data"
COLLECTED_DATA_CSV = RESULTS_DIR / "vehicle_auth_data.csv"
COLLECTED_EXCHANGED_DATA_CSV = RESULTS_DIR / "vehicle_exchanged_data.csv"

# === Smart Contract Addresses ===
CONTRACTS_DIR = BASE_DIR / "static" / "Data" / "build" / "contracts"
ADDRESS_ONE = CONTRACTS_DIR / "BC1.json"
ADDRESS_TWO = CONTRACTS_DIR / "BC2.json"
ADDRESS_THREE = CONTRACTS_DIR / "BC3.json"
