"""
Caesar Cipher Implementation
A simple substitution cipher that shifts letters by a fixed number
"""

class CaesarCipher:
    """Caesar cipher encryption and decryption"""
    
    @staticmethod
    def encrypt(plaintext, shift):
        """
        Encrypt plaintext using Caesar cipher
        
        Args:
            plaintext (str): Text to encrypt
            shift (int): Number of positions to shift
            
        Returns:
            str: Encrypted text
        """
        if not isinstance(shift, int):
            try:
                shift = int(shift)
            except:
                raise ValueError("Shift must be an integer")
        
        # Validate shift range
        if shift < 0 or shift > 26:
            raise ValueError("Shift must be between 0 and 26")
        
        # Normalize shift to 0-25 range
        shift = shift % 26
        
        encrypted = ""
        
        for char in plaintext:
            if char.isalpha():
                # Determine if uppercase or lowercase
                ascii_offset = ord('A') if char.isupper() else ord('a')
                
                # Shift character
                shifted = (ord(char) - ascii_offset + shift) % 26
                encrypted += chr(shifted + ascii_offset)
            else:
                # Keep non-alphabetic characters unchanged
                encrypted += char
        
        return encrypted
    
    @staticmethod
    def decrypt(ciphertext, shift):
        """
        Decrypt ciphertext using Caesar cipher
        
        Args:
            ciphertext (str): Text to decrypt
            shift (int): Number of positions to shift back
            
        Returns:
            str: Decrypted text
        """
        if not isinstance(shift, int):
            try:
                shift = int(shift)
            except:
                raise ValueError("Shift must be an integer")
        
        # Validate shift range
        if shift < 0 or shift > 26:
            raise ValueError("Shift must be between 0 and 26")
            
        # Decryption is encryption with negative shift (normalized)
        return CaesarCipher.encrypt(ciphertext, (26 - shift) % 26)
    
    @staticmethod
    def brute_force(ciphertext):
        """
        Attempt all possible shifts (brute force attack)
        
        Args:
            ciphertext (str): Text to decrypt
            
        Returns:
            list: All possible decryptions with their shifts
        """
        results = []
        
        for shift in range(26):
            decrypted = CaesarCipher.decrypt(ciphertext, shift)
            results.append({
                'shift': shift,
                'text': decrypted
            })
        
        return results


# Example usage and testing
if __name__ == "__main__":
    # Test encryption
    plaintext = "Hello World"
    shift = 3
    
    encrypted = CaesarCipher.encrypt(plaintext, shift)
    print(f"Plaintext: {plaintext}")
    print(f"Shift: {shift}")
    print(f"Encrypted: {encrypted}")
    
    # Test decryption
    decrypted = CaesarCipher.decrypt(encrypted, shift)
    print(f"Decrypted: {decrypted}")
    
    # Test brute force
    print("\nBrute Force Attack:")
    results = CaesarCipher.brute_force(encrypted)
    for result in results[:5]:  # Show first 5
        print(f"Shift {result['shift']}: {result['text']}")
