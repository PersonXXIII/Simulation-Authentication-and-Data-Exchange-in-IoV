import hashlib
import json
import os
import random
import string

base_dir = os.path.dirname(os.path.abspath(__file__))

# Directory to store the generated credentials
CREDENTIALS_DIR = os.path.join(base_dir, "Auth_N_Credentials")

# Ensure the credentials directory exists
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

def generate_static_credentials(auth_n_id, entity_type):
    """
    Generate static credentials for a given Auth_N entity.
    :param auth_n_id: Unique ID for the Auth_N entity.
    :param entity_type: Type of the entity ("EC" or "RSU").
    :return: A dictionary containing the ID, type, and hashed password.
    """
    # Static username and password generation
    username = f"Auth_{auth_n_id}_{entity_type}"
    password = f"Pass_{auth_n_id}"  # Static password for simplicity

    # Hash the password for secure storage
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    return {
        "auth_n_id": auth_n_id,
        "entity_type": entity_type,
        "username": username,
        "password_hash": password_hash
    }

def generate_fake_credentials(fake_id):
    """
    Generate credentials for a fake/hacker Auth_N entity.
    :param fake_id: Unique ID for the fake Auth_N entity.
    :return: A dictionary with fake credentials.
    """
    username = f"Hacker_{fake_id}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Random password
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    return {
        "auth_n_id": fake_id,
        "entity_type": "Fake",
        "username": username,
        "password": password,  # Storing plaintext password for debugging
        "password_hash": password_hash
    }

def save_credentials(auth_n_credentials):
    """
    Save the generated credentials to a file in JSON format.
    :param auth_n_credentials: List of credential dictionaries.
    """
    for cred in auth_n_credentials:
        filename = os.path.join(CREDENTIALS_DIR, f"Auth_{cred['auth_n_id']}.json")
        with open(filename, 'w') as f:
            json.dump(cred, f, indent=4)

    print(f"Credentials saved in '{CREDENTIALS_DIR}' directory.")

def main_generate(num_auth_n):
    """
    Generate and save credentials for Auth_N entities.
    :param num_auth_n: Total number of Auth_N entities to generate.
    """
    if num_auth_n < 1:
        print("The number of Auth_N entities must be at least 1.")
        return

    credentials = []

    # Generate 1 EC credential
    credentials.append(generate_static_credentials(1, "EC"))

    # Generate the remaining RSU credentials
    for i in range(2, num_auth_n + 1):
        credentials.append(generate_static_credentials(i, "RSU"))

    # Generate 1 fake/hacker Auth_N credential
    fake_id = num_auth_n + 1
    fake_credential = generate_fake_credentials(fake_id)
    credentials.append(fake_credential)

    # Save the credentials to files
    save_credentials(credentials)

    # Display the fake credential details for debugging
    json.dumps(fake_credential, indent=4)

if __name__ == "__main__":
    try:
        num_auth_n = int(input("Enter the total number of Auth_N entities to generate: "))
        main_generate(num_auth_n)
    except ValueError:
        print("Invalid input. Please enter an integer value.")
