from ecdsa import SigningKey, VerifyingKey, NIST256p
import hashlib
import binascii
import pandas as pd

# Function to hash the VIN using SHA-256
def hash_vin(vin):
    return hashlib.sha256(vin.encode()).digest()

# Function to generate a deterministic signature
def generate_proof(private_key_hex, hashed_vin):
    private_key_bytes = binascii.unhexlify(private_key_hex)  # Convert hex to bytes
    private_key = SigningKey.from_string(private_key_bytes, curve=NIST256p)
    return private_key.sign_deterministic(hashed_vin)

# Function to verify the signature (proof)
def verify_proof(public_key_hex, hashed_vin, signature):
    public_key_bytes = binascii.unhexlify(public_key_hex)  # Convert hex to bytes
    public_key = VerifyingKey.from_string(public_key_bytes, curve=NIST256p)
    try:
        return public_key.verify(signature, hashed_vin)
    except Exception as e:
        print("Verification failed:", e)
        return False

# Process CSV to add hashed VIN and proof
def process_csv_add_proof(input_file, output_file):
    # Read the input CSV
    data = pd.read_csv(input_file)

    # Prepare lists to store results
    hashed_vins = []
    proofs = []

    # Process each row
    for index, row in data.iterrows():
        vin = row['VIN']  # Assuming the CSV has a column named 'VIN'
        private_key_hex = row['Private Key']  # Assuming the CSV has a column named 'PrivateKey'

        # Hash the VIN
        hashed_vin = hash_vin(vin)
        hashed_vins.append(hashed_vin.hex())

        # Generate proof
        proof = generate_proof(private_key_hex, hashed_vin)
        proofs.append(proof.hex())

    # Add results to the dataframe
    data['Hashed VIN'] = hashed_vins
    data['Proof'] = proofs

    # Save to output file
    data.to_csv(output_file, index=False)

# Example usage
if __name__ == "__main__":
    # Input and output file paths
    input_csv = "Pre_Final.csv"  # Replace with your input file path
    output_csv = "Final.csv"  # Replace with your desired output file path

    # Process the CSV
    process_csv_add_proof(input_csv, output_csv)
    print(f"Processed data with proofs saved to {output_csv}")
    
# a5992d3063df37eda9d74573e3a6293a121d6e012359e4b8a188bbaa76a216c478e52cee8b3fc7c4a8877ffb5afcac2f15c5e5e7d2b94058b59821a600641c6c
# a5992d3063df37eda9d74573e3a6293a121d6e012359e4b8a188bbaa76a216c478e52cee8b3fc7c4a8877ffb5afcac2f15c5e5e7d2b94058b59821a600641c6c