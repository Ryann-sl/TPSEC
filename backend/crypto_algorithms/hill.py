"""
Hill Cipher Implementation
A polygraphic substitution cipher using linear algebra
"""

import numpy as np

class HillCipher:
    """Hill cipher encryption and decryption"""
    
    @staticmethod
    def text_to_numbers(text):
        """Convert text to numbers (A=0, B=1, ..., Z=25)"""
        text = text.upper().replace(' ', '')
        return [ord(char) - ord('A') for char in text if char.isalpha()]
    
    @staticmethod
    def numbers_to_text(numbers):
        """Convert numbers back to text"""
        return ''.join([chr(num % 26 + ord('A')) for num in numbers])
    
    @staticmethod
    def prepare_key_matrix(key_string, size=2):
        """
        Prepare key matrix from string
        
        Args:
            key_string (str): Key string (must have size*size characters)
            size (int): Matrix size (default 2x2)
            
        Returns:
            numpy.ndarray: Key matrix
        """
        key_numbers = HillCipher.text_to_numbers(key_string)
        
        if len(key_numbers) < size * size:
            # Pad with zeros if too short
            key_numbers.extend([0] * (size * size - len(key_numbers)))
        
        key_numbers = key_numbers[:size * size]
        
        return np.array(key_numbers).reshape(size, size)
    
    @staticmethod
    def mod_inverse(matrix, modulus=26):
        """
        Calculate modular inverse of matrix
        
        Args:
            matrix (numpy.ndarray): Matrix to invert
            modulus (int): Modulus (default 26 for alphabet)
            
        Returns:
            numpy.ndarray: Inverse matrix or None if not invertible
        """
        det = int(np.round(np.linalg.det(matrix)))
        det_inv = None
        
        # Find modular inverse of determinant
        for i in range(modulus):
            if (det * i) % modulus == 1:
                det_inv = i
                break
        
        if det_inv is None:
            return None
        
        # Calculate matrix inverse
        matrix_inv = det_inv * np.round(det * np.linalg.inv(matrix)).astype(int)
        
        return matrix_inv % modulus
    
    @staticmethod
    def encrypt(plaintext, key_string):
        """
        Encrypt plaintext using Hill cipher
        
        Args:
            plaintext (str): Text to encrypt
            key_string (str): Key string (4 characters for 2x2 matrix)
            
        Returns:
            str: Encrypted text
        """
        # Prepare key matrix (2x2)
        key_matrix = HillCipher.prepare_key_matrix(key_string, 2)
        
        # Convert text to numbers
        numbers = HillCipher.text_to_numbers(plaintext)
        
        # Pad if odd length
        if len(numbers) % 2 != 0:
            numbers.append(23)  # Add 'X'
        
        encrypted_numbers = []
        
        # Encrypt in blocks of 2
        for i in range(0, len(numbers), 2):
            block = np.array(numbers[i:i+2])
            encrypted_block = np.dot(key_matrix, block) % 26
            encrypted_numbers.extend(encrypted_block.tolist())
        
        return HillCipher.numbers_to_text(encrypted_numbers)
    
    @staticmethod
    def decrypt(ciphertext, key_string):
        """
        Decrypt ciphertext using Hill cipher
        
        Args:
            ciphertext (str): Text to decrypt
            key_string (str): Key string (4 characters for 2x2 matrix)
            
        Returns:
            str: Decrypted text or error message
        """
        # Prepare key matrix
        key_matrix = HillCipher.prepare_key_matrix(key_string, 2)
        
        # Calculate inverse matrix
        inv_matrix = HillCipher.mod_inverse(key_matrix)
        
        if inv_matrix is None:
            return "ERROR: Key matrix is not invertible"
        
        # Convert text to numbers
        numbers = HillCipher.text_to_numbers(ciphertext)
        
        decrypted_numbers = []
        
        # Decrypt in blocks of 2
        for i in range(0, len(numbers), 2):
            if i + 1 < len(numbers):
                block = np.array(numbers[i:i+2])
                decrypted_block = np.dot(inv_matrix, block) % 26
                decrypted_numbers.extend(decrypted_block.tolist())
        
        return HillCipher.numbers_to_text(decrypted_numbers)


# Example usage
if __name__ == "__main__":
    plaintext = "HELP"
    key = "HILL"  # 2x2 matrix: H=7, I=8, L=11, L=11
    
    print(f"Plaintext: {plaintext}")
    print(f"Key: {key}")
    
    encrypted = HillCipher.encrypt(plaintext, key)
    print(f"Encrypted: {encrypted}")
    
    decrypted = HillCipher.decrypt(encrypted, key)
    print(f"Decrypted: {decrypted}")
