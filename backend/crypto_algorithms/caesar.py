"""
Caesar Cipher Implementation (Simple Educational Version)
Follows the requirements for the PFE Security Platform.
"""

class CaesarCipher:
    """A clean, simple implementation of the Caesar Cipher for students."""
    
    @staticmethod
    def encrypt(text, shift):
        """
        ENCRYPTION: Shift letters FORWARD (P + K) mod 26
        """
        # Normalize and detect weak keys
        normalized_shift = shift % 26
        if normalized_shift == 0:
            raise ValueError("Weak Key Detected: A shift of 0 (or 26) provides no encryption.")
            
        result = ""
        for char in text:
            if char.isupper():
                # (Current Position + Shift) wrapped at 26
                new_pos = (ord(char) - ord('A') + normalized_shift) % 26
                result += chr(new_pos + ord('A'))
            elif char.islower():
                new_pos = (ord(char) - ord('a') + normalized_shift) % 26
                result += chr(new_pos + ord('a'))
            else:
                result += char
        return result

    @staticmethod
    def decrypt(text, shift):
        """
        DECRYPTION: Shift letters BACKWARD (C - K) mod 26
        """
        # Normalize and detect weak keys
        normalized_shift = shift % 26
        if normalized_shift == 0:
            raise ValueError("Weak Key Detected: A shift of 0 (or 26) provides no encryption.")
            
        result = ""
        for char in text:
            if char.isupper():
                # (Current Position - Shift) wrapped at 26
                new_pos = (ord(char) - ord('A') - normalized_shift) % 26
                result += chr(new_pos + ord('A'))
            elif char.islower():
                new_pos = (ord(char) - ord('a') - normalized_shift) % 26
                result += chr(new_pos + ord('a'))
            else:
                result += char
        return result

    @staticmethod
    def brute_force(text):
        """
        Try all 25 possible shifts to find the message.
        """
        possible_results = []
        for s in range(1, 26):
            possible_results.append({
                'shift': s,
                'result': CaesarCipher.decrypt(text, s)
            })
        return possible_results

# Simple Test Cases (Matching the User Table)
if __name__ == "__main__":
    # Test 1: Wrap-around
    print(f"XYZ + 3 = {CaesarCipher.encrypt('XYZ', 3)}") # Expected: ABC
    
    # Test 2: Case sensitivity
    print(f"Hello + 3 = {CaesarCipher.encrypt('Hello', 3)}") # Expected: Khoor
    
    # Test 3: Non-alphabet chars
    print(f"H! + 3 = {CaesarCipher.encrypt('H!', 3)}") # Expected: K!
    
    # Test 4: Weak Keys
    print(f"HELLO + 26 = {CaesarCipher.encrypt('HELLO', 26)}") # Expected: HELLO (Weak Key)
