import uuid
import secrets
import json

def generate_temp_vehicle_id():
    """Generate a temporary vehicle ID."""
    return f"TEMP_ID_{uuid.uuid4().hex[:8].upper()}"  # Shortened UUID for uniqueness

def generate_session_key(length=16):
    """Generate a secure session key."""
    return secrets.token_hex(length // 2)  # Convert bytes to hex (length should be even)

if __name__ == "__main__":
    # Generate the values
    temp_vehicle_id = generate_temp_vehicle_id()
    session_key = generate_session_key()

    # Return as a JSON string
    result = {
        "temp_vehicle_ID": temp_vehicle_id,
        "sessionKey": session_key
    }
    print(json.dumps(result))  # Print the result in JSON format for the calling script
