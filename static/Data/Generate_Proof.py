from ecdsa import SigningKey, VerifyingKey, NIST256p
import hashlib
import binascii

# Function to hash the VIN using SHA-256
def hash_vin(vin):
    try:
        return hashlib.sha256(vin.encode()).digest()
    except Exception as e:
        raise ValueError(f"Error hashing VIN: {str(e)}")

# Function to generate a deterministic signature
def generate_proof(private_key_hex, hashed_vin):
    try:
        # Ensure private_key_hex is valid hex and of even length
        if len(private_key_hex) % 2 != 0:
            private_key_hex = "0" + private_key_hex  # Padding the PrivateKey if it's odd-length
        
        # Check if the private key is 64 hex characters (32 bytes)
        if len(private_key_hex) != 64:
            raise ValueError(f"Invalid length of private key, received {len(private_key_hex)}, expected 64")
        
        # Convert hex to bytes
        private_key_bytes = binascii.unhexlify(private_key_hex)  # Convert hex to bytes
        
        # Generate the private key from the bytes
        private_key = SigningKey.from_string(private_key_bytes, curve=NIST256p)
        
        # Sign the hash of VIN deterministically
        return private_key.sign_deterministic(hashed_vin)
    
    except binascii.Error:
        raise ValueError("Invalid hexadecimal characters in private key.")
    except Exception as e:
        raise ValueError(f"Error during proof generation: {str(e)}")

# Function to verify the signature (proof)
def verify_proof(public_key_hex, hashed_vin, signature):
    try:
        public_key_bytes = binascii.unhexlify(public_key_hex)  # Convert hex to bytes
        public_key = VerifyingKey.from_string(public_key_bytes, curve=NIST256p)
        return public_key.verify(signature, hashed_vin)
    except Exception as e:
        print("Verification failed:", e)
        return False

# Class to handle proof generation
class GenerateProof:
    
    @staticmethod
    def process_proof(vin, private_key_hex):
        try:
            # Hash the VIN
            hashed_vin = hash_vin(vin)
            hashed_vins = hashed_vin.hex()

            # Generate proof (deterministic signature)
            proof = generate_proof(private_key_hex, hashed_vin)
            proofs = proof.hex()

            return hashed_vins, proofs
        except Exception as e:
            print(f"Error processing proof: {str(e)}")
            return None, None
