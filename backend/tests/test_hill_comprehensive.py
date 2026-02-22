import sys
import os
import time

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_algorithms.hill import HillCipher

def run_test(name, result):
    if result:
        print(f"✅ {name}: PASSED")
    else:
        print(f"❌ {name}: FAILED")

def test_hill_comprehensive():
    print("🚀 Starting Comprehensive Hill Cipher Test Suite\n")

    # 1. Basic Functionality
    # Case 1: Standard 2x2
    k1 = [[3, 3], [2, 5]]
    enc1 = HillCipher.encrypt("HI", k1)
    run_test("Case 1: Standard 2x2 Encryption", enc1 == "TC")
    run_test("Case 14: Standard 2x2 Decryption", HillCipher.decrypt("TC", k1) == "HI")

    # Case 2: Multi-block 2x2
    k2 = [[7, 8], [11, 11]]
    enc2 = HillCipher.encrypt("HELLO", k2)
    dec2 = HillCipher.decrypt(enc2, k2)
    run_test("Case 2: Multi-block 2x2 (HELLO)", dec2 == "HELLOX") # X is padding

    # Case 3: 3x3 Matrix
    k3 = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
    enc3 = HillCipher.encrypt("ABC", k3)
    run_test("Case 3: 3x3 Encryption", HillCipher.decrypt(enc3, k3) == "ABC")

    # 2. Determinant Edge Cases
    # Case 4: det=0 mod 26
    try:
        # matrix [[2, 4], [6, 12]] -> det = 24-24=0
        HillCipher.encrypt("HI", [[2, 4], [6, 12]])
        run_test("Case 4: Det=0 Rejected", False)
    except ValueError:
        run_test("Case 4: Det=0 Rejected", True)

    # Case 5: det shared factor with 26 (det=22 -> gcd(22,26)=2)
    try:
        # matrix [[2, 4], [6, 10]] -> det = 20-24=-4 -> 22 mod 26
        HillCipher.encrypt("HI", [[2, 4], [6, 10]])
        run_test("Case 5: Det shared factor rejected", False)
    except ValueError:
        run_test("Case 5: Det shared factor rejected", True)

    # 3. Modular Wrap-around
    # Case 6: ZZ (25, 25)
    k6 = [[5, 7], [3, 2]]
    enc6 = HillCipher.encrypt("ZZ", k6)
    run_test("Case 6: Mod 26 Wrap-around (ZZ)", HillCipher.decrypt(enc6, k6) == "ZZ")

    # 4. Input Validation
    # Case 8: Lowercase
    run_test("Case 8: Lowercase Normalization", HillCipher.encrypt("Hi", k1) == "TC")
    
    # Case 9: Symbols and Numbers
    run_test("Case 9: Ignore Symbols/Numbers", HillCipher.encrypt("HELLO 123!", k1) == HillCipher.encrypt("HELLO", k1))

    # 5. Known Plaintext Attack (Simulation)
    # Case 10: Attacker knows HI->TC and BY->XS
    recovered_k = HillCipher.solve_key("HIBY", "TCXS", 2)
    # recovered_k should match k1 [[3, 3], [2, 5]]
    run_test("Case 10: Known Plaintext Attack Recovery", recovered_k == k1)

    # 7. Padding
    # Case 12: HELLO (5 chars) -> 6 chars with X
    enc12 = HillCipher.encrypt("HELLO", k1)
    run_test("Case 12: Padding handled (HELLO -> HELLOX)", len(enc12) == 6)

    # 9. Performance
    # Case 16: 100 letters
    large_text = "A" * 100
    start = time.time()
    enc16 = HillCipher.encrypt(large_text, k3)
    end = time.time()
    run_test("Case 16: Performance 100-letter text", (end-start) < 0.1)

    # 10. Invalid Key Handling
    # Case 18: Non-square
    try:
        HillCipher.prepare_key_matrix([[1, 2, 3], [4, 5, 6]])
        run_test("Case 18: Non-square rejected", False)
    except ValueError:
        run_test("Case 18: Non-square rejected", True)

    # Case 19: Non-integer entries
    try:
        HillCipher.prepare_key_matrix([[1.5, 2], [3, 4]])
        run_test("Case 19: Non-integer rejected", False)
    except ValueError:
        run_test("Case 19: Non-integer rejected", True)

    # Case 20: Empty key
    try:
        HillCipher.prepare_key_matrix([])
        run_test("Case 20: Empty key rejected", False)
    except ValueError:
        run_test("Case 20: Empty key rejected", True)

    # 11. All Letters Coverage
    # Case 21: A-Z
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    enc21 = HillCipher.encrypt(alphabet, k3)
    dec21 = HillCipher.decrypt(enc21, k3)
    run_test("Case 21: Alphabet A-Z correctly processed", dec21.startswith(alphabet))

    print("\n🏁 Comprehensive Test Suite Completed")

if __name__ == "__main__":
    test_hill_comprehensive()
