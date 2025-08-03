from ecdsa import SigningKey, NIST256p
import hashlib
import base64
import pandas as pd

# Function to generate ECC key pair
def generate_ecc_keys():
    private_key = SigningKey.generate(curve=NIST256p)
    public_key = private_key.verifying_key
    return private_key, public_key

# Function to encrypt the VIN using the public key
def encrypt_vin(vin, public_key):
    hashed_vin = hashlib.sha256(vin.encode()).digest()
    encrypted_vin = base64.b64encode(hashed_vin).decode()  # Simulating encryption for simplicity
    return encrypted_vin

# Process CSV and generate keys and encrypted VINs
def process_csv(input_file, output_file):
    # Read the input CSV
    data = pd.read_csv(input_file)

    # Prepare lists to store results
    private_keys = []
    public_keys = []
    encrypted_vins = []

    # Process each row
    for index, row in data.iterrows():
        vin = row['VIN']

        # Generate ECC keys
        private_key, public_key = generate_ecc_keys()

        # Encrypt VIN
        encrypted_vin = encrypt_vin(vin, public_key)

        # Store results
        private_keys.append(private_key.to_string().hex())
        public_keys.append(public_key.to_string().hex())
        encrypted_vins.append(encrypted_vin)

    # Add results to the dataframe
    data['Private Key'] = private_keys
    data['Public Key'] = public_keys
    data['Encrypted VIN'] = encrypted_vins

    # Save to output file
    data.to_csv(output_file, index=False)

# Example usage
if __name__ == "__main__":
    # Input and output file paths
    input_csv = "Updated_Data.csv"  # Replace with your input file path
    output_csv = "Pre_Final.csv"  # Replace with your desired output file path

    # Process the CSV
    process_csv(input_csv, output_csv)
    print(f"Processed data saved to {output_csv}")