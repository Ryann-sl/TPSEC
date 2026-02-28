import sys
import os

# Add current directory to path so crypto_algorithms can be imported
sys.path.append(os.path.dirname(__file__))

from crypto_algorithms.hill import HillCipher

def debug_hill_key():
    key = "HILL"
    plaintext = "HELP"
    
    # Simulate step-by-step
    numbers = HillCipher.text_to_numbers(key)
    print(f"Key numbers for '{key}': {numbers}")
    
    n = int(len(numbers)**0.5)
    print(f"Inferred size n: {n}")
    
    K = HillCipher.prepare_key_matrix(key, n)
    print(f"Key matrix K: {K}")
    
    det = HillCipher.get_determinant(K)
    print(f"Determinant: {det}")
    print(f"Determinant mod 26: {det % 26}")
    
    try:
        enc = HillCipher.encrypt(plaintext, key)
        print(f"Encrypted '{plaintext}': {enc}")
    except Exception as e:
        print(f"Encryption failed: {e}")

if __name__ == "__main__":
    debug_hill_key()
