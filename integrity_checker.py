import hashlib 
import os

def generate_file_hash(file_path):
    """
    Takes in a file as a parameter to generate a SHA-256 hash.
    Read in chunks to handle large video files without crashing the RAM
    """

    # Initialize the SHA-256 hashing algorithm
    sha256_hash = hashlib.sha256()

    try:
        #open the file in binary mode ('rb') to read raw data
        with open(file_path, "rb") as f: 
            #read the file in 4096 byte blocks
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

            #return the final hash as a hexadecimal string
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def verify_media_integrity(reference_hash, file_to_check):
    """
    Compares the original hash with the hash of the newly uploaded file.
    """
    current_hash= generate_file_hash(file_to_check)

    if current_hash is None:
        return False, None
    
    if reference_hash==current_hash: 
        return True, current_hash  #Integrity maintained
    else: 
        return False, current_hash  #Integrity compromised
    
    # SIMULATION / PROTOTYPE TEST SCRIPT

if __name__ == "__main__": 
        print("--- DeepShield: Media Integrity Verification Module ---\n")

        # step 1: create dummy file for simulation
        test_media = "sample_video_data.txt"

        with open(test_media, "w") as f:
            f.write("This is the original, authentic video frame data")

        #step 2: generate the 'reference hash' (simulating the baseline creation)
        print("[*] Generating baseline hash for original media...")
        baseline_hash = generate_file_hash(test_media)
        print(f"Original SHA-256 Hash: {baseline_hash}\n")

        #step 3: verify the unmodified file
        print("[*] Verifying unmodified file...")
        is_valid, current_hash= verify_media_integrity(baseline_hash, test_media)
        print(f"Result: {'INTEGRITY VERIFIED' if is_valid else 'ALERT: HAS BEEN MODIFIED'} \n")

        #step 4: simulate an attacker altering the deepfake media
        print("[!] Attacker alters the media file (injecting deepfake data)...")
        with open(test_media, "a") as f: 
            f.write("[Deepfake pixel data injected here]")

        #step 5: verify the tampered file
        is_valid, current_hash = verify_media_integrity(baseline_hash, test_media)
        print(f"New SHA-256 Hash: {current_hash}")
        print(f"Result: {'INTEGRITY VERIFIED' if is_valid else 'ALERT: MEDIA HAS BEEN MODIFIED'} \n")