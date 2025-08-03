import csv
import random
from math import floor
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv
import string

# Load the environment variables from the .env file
load_dotenv()

def generate_bad_twins(dt_client, model_id, rows, num_good_twins, num_bad_twins, log_file):
    """
    Generate bad twins by altering fields from the given rows.

    :param dt_client: Azure DigitalTwinsClient instance.
    :param model_id: Model ID for the twins.
    :param rows: List of rows from the CSV.
    :param num_good_twins: Number of good twins already generated.
    :param num_bad_twins: Number of bad twins to generate.
    :param log_file: Path to the log file for recording alterations.
    :return: List of bad twin IDs.
    """
    twin_ids = []

    with open(log_file, mode='w') as log:
        for i in range(1, num_bad_twins + 1):
            twin_id = f"V{num_good_twins + i}"  # Generate twin names like V5, V6, etc.
            row = random.choice(rows)  # Select a random row from the CSV
            alteration = random.choice(["VIN", "PrivateKey"])  # Randomly pick a field to alter
            original_data = {
                "VIN": row.get("VIN", "Unknown"),
                "PublicKey": row.get("Public Key", "Unknown"),
                "PrivateKey": row.get("Private Key", "Unknown"),
            }
            
            altered_data = original_data.copy()
            if alteration == "VIN":
                altered_data["VIN"] = replace_last_digit(original_data["VIN"])
            elif alteration == "PrivateKey":
                altered_data["PrivateKey"] = replace_last_digit(original_data["PrivateKey"])

            twin_data = {
                "$metadata": {
                    "$model": model_id  # Specify the model ID in the metadata
                },
                "VIN": altered_data["VIN"],
                "Name": row.get("Brand", "Unknown"),
                "Model": row.get("Model", "Unknown"),
                "PrivateKey": altered_data["PrivateKey"],
            }

            try:
                # Create or update the twin in Azure Digital Twins
                dt_client.upsert_digital_twin(twin_id, twin_data)
                print(f"Successfully created/updated BAD twin with ID: {twin_id}")
                twin_ids.append(twin_id)

                # Log the alteration with original and altered data
                log.write(
                    f"{twin_id} {alteration} was altered. Original Data: {original_data}, Altered Data: {altered_data}\n"
                )
            except Exception as e:
                print(f"Failed to create/update BAD twin with ID {twin_id}: {e}")

    return twin_ids

def generate_twins_from_csv(num_rows):
    """
    Reads a predefined CSV file, selects a random subset of rows, and generates twins in Azure Digital Twins.
    Generates both correct and incorrect twins based on the input number.

    :param num_rows: Number of rows to use for generating twins (both correct and incorrect).
    """
    
    # Get the current directory where the script is running
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    csv_file_path = os.path.join(base_dir, "Final.csv")
    model_id = "dtmi:SimulationForIoV:Vehicle;1"  # Static model ID for creating twins
    dt_client = DigitalTwinsClient(
        "https://SimulationForIoV.api.wcus.digitaltwins.azure.net", DefaultAzureCredential()
    )
    twin_ids = []
    log_file = os.path.join(base_dir, "bad_twin_log.txt")

    try:
        # Read CSV file
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        # Check if the number of rows requested exceeds the available rows
        if num_rows > len(rows):
            raise ValueError("Requested number of rows exceeds the available rows in the CSV file.")

        # Determine the number of bad twins to generate
        num_bad_twins = max(1, floor(num_rows / 2))  # At least 1 bad twin for odd numbers or parameter = 1
        num_good_twins = num_rows

        # Generate good twins
        for i, row in enumerate(random.sample(rows, num_good_twins), start=1):
            twin_id = f"V{i}"  # Generate twin names like V1, V2, etc.
            twin_data = {
                "$metadata": {
                    "$model": model_id  # Specify the model ID in the metadata
                },
                "VIN": row.get("VIN", "Unknown"),
                "Name": row.get("Brand", "Unknown"),
                "Model": row.get("Model", "Unknown"),
                "PublicKey": row.get("Public Key", "Unknown"),
                "PrivateKey": row.get("Private Key", "Unknown"),
            }

            try:
                # Create or update the twin in Azure Digital Twins
                dt_client.upsert_digital_twin(twin_id, twin_data)
                print(f"Successfully created/updated GOOD twin with ID: {twin_id}")
                twin_ids.append(twin_id)
            except Exception as e:
                print(f"Failed to create/update GOOD twin with ID {twin_id}: {e}")

        # Generate bad twins
        twin_ids.extend(generate_bad_twins(dt_client, model_id, rows, num_good_twins, num_bad_twins, log_file))

    except FileNotFoundError:
        print("The specified CSV file was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    random.shuffle(twin_ids)
    return twin_ids

import random
import string

def replace_last_digit(value):
    if not value:  # If empty, return unchanged
        return value  

    last_char = value[-1]

    # Define valid hexadecimal characters
    hex_chars = "0123456789abcdef"

    if last_char in hex_chars:  # If last character is valid hex
        # Pick a different valid hex character (ensuring it's not the same as the original)
        new_last_char = random.choice([ch for ch in hex_chars if ch != last_char])

    else:  # If last character is neither a valid hex character, return unchanged
        return value  

    return value[:-1] + new_last_char  # Replace last character


