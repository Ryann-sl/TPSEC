"""
Caesar Cipher Implementation (Simple Educational Version)
Follows the requirements for the PFE Security Platform.
"""

class CaesarCipher:
    """A clean, simple implementation of the Caesar Cipher for students."""
    
    @staticmethod
    def encrypt(text, shift, direction='right'):
        """
        ENCRYPTION: Shift letters (P + K) mod 26
        """
        # Ensure shift is non-negative and normalize
        shift = abs(int(shift))
        normalized_shift = shift % 26
        
        # Adjust shift based on direction
        if direction.lower() == 'left':
            actual_shift = -normalized_shift
        else:
            actual_shift = normalized_shift

        if normalized_shift == 0:
            raise ValueError("Weak Key Detected: A shift of 0 (or 26) provides no encryption.")
            
        result = ""
        for char in text:
            if char.isupper():
                new_pos = (ord(char) - ord('A') + actual_shift) % 26
                result += chr(new_pos + ord('A'))
            elif char.islower():
                new_pos = (ord(char) - ord('a') + actual_shift) % 26
                result += chr(new_pos + ord('a'))
            else:
                result += char
        return result

    @staticmethod
    def decrypt(text, shift, direction='right'):
        """
        DECRYPTION: Shift letters BACKWARD (C - K) mod 26
        """
        # For decryption, we effectively reverse the encryption shift
        # Encryption of 'A' (0) with shift 3 Right is 'D' (3)
        # Decryption of 'D' (3) with shift 3 Right should be 'A' (0) -> Shift 3 Left
        
        # We can just call encrypt with the opposite direction!
        # BUT, standard Caesar decryption (C - K) usually means "Shift back by K"
        # If the user says "Shift 3 Right" for encryption, decryption should "Shift 3 Left"
        # This implementation will treat the direction as the *intended* shift direction.
        
        shift = abs(int(shift))
        normalized_shift = shift % 26
        
        if normalized_shift == 0:
            raise ValueError("Weak Key Detected: A shift of 0 (or 26) provides no encryption.")
            
        # Standard decryption: (pos - shift) % 26
        # If encrypted with 'right', we decrypt by moving 'left'
        # If encrypted with 'left', we decrypt by moving 'right'
        
        if direction.lower() == 'left':
            actual_shift = normalized_shift # Reverse of left shift is right shift
        else:
            actual_shift = -normalized_shift # Reverse of right shift is left shift

        result = ""
        for char in text:
            if char.isupper():
                new_pos = (ord(char) - ord('A') + actual_shift) % 26
                result += chr(new_pos + ord('A'))
            elif char.islower():
                new_pos = (ord(char) - ord('a') + actual_shift) % 26
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
