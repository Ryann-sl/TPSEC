"""
Playfair Cipher Implementation
A digraph substitution cipher using a 5x5 key matrix
"""

class PlayfairCipher:
    """Playfair cipher encryption and decryption"""
    
    @staticmethod
    def prepare_key(keyword):
        """
        Create 5x5 key matrix from keyword
        
        Args:
            keyword (str): Keyword for the cipher
            
        Returns:
            list: 5x5 matrix
        """
        # Remove duplicates and convert to uppercase
        keyword = keyword.upper().replace('J', 'I')
        seen = set()
        key_chars = []
        
        for char in keyword:
            if char.isalpha() and char not in seen:
                seen.add(char)
                key_chars.append(char)
        
        # Add remaining letters
        for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":  # No J
            if char not in seen:
                key_chars.append(char)
        
        # Create 5x5 matrix
        matrix = []
        for i in range(5):
            matrix.append(key_chars[i*5:(i+1)*5])
        
        return matrix
    
    @staticmethod
    def find_position(matrix, char):
        """Find position of character in matrix"""
        for i, row in enumerate(matrix):
            for j, c in enumerate(row):
                if c == char:
                    return i, j
        return None, None
    
    @staticmethod
    def prepare_text(text):
        """
        Prepare text for encryption
        - Remove spaces and convert to uppercase
        - Replace J with I
        - Split into digraphs
        - Add X between duplicate letters
        """
        text = text.upper().replace('J', 'I').replace(' ', '')
        
        # Split into pairs
        pairs = []
        i = 0
        while i < len(text):
            if i == len(text) - 1:
                # Add X to last character if odd length
                pairs.append(text[i] + 'X')
                i += 1
            elif text[i] == text[i+1]:
                # Add X between duplicates
                pairs.append(text[i] + 'X')
                i += 1
            else:
                pairs.append(text[i:i+2])
                i += 2
        
        return pairs
    
    @staticmethod
    def encrypt(plaintext, keyword):
        """
        Encrypt plaintext using Playfair cipher
        
        Args:
            plaintext (str): Text to encrypt
            keyword (str): Keyword for the cipher
            
        Returns:
            str: Encrypted text
        """
        if not keyword:
            raise ValueError("Keyword is required")
        
        matrix = PlayfairCipher.prepare_key(keyword)
        pairs = PlayfairCipher.prepare_text(plaintext)
        
        encrypted = ""
        
        for pair in pairs:
            row1, col1 = PlayfairCipher.find_position(matrix, pair[0])
            row2, col2 = PlayfairCipher.find_position(matrix, pair[1])
            
            if row1 == row2:
                # Same row: shift right
                encrypted += matrix[row1][(col1 + 1) % 5]
                encrypted += matrix[row2][(col2 + 1) % 5]
            elif col1 == col2:
                # Same column: shift down
                encrypted += matrix[(row1 + 1) % 5][col1]
                encrypted += matrix[(row2 + 1) % 5][col2]
            else:
                # Rectangle: swap columns
                encrypted += matrix[row1][col2]
                encrypted += matrix[row2][col1]
        
        return encrypted
    
    @staticmethod
    def decrypt(ciphertext, keyword):
        """
        Decrypt ciphertext using Playfair cipher
        
        Args:
            ciphertext (str): Text to decrypt
            keyword (str): Keyword for the cipher
            
        Returns:
            str: Decrypted text
        """
        if not keyword:
            raise ValueError("Keyword is required")
        
        matrix = PlayfairCipher.prepare_key(keyword)
        ciphertext = ciphertext.upper().replace(' ', '')
        
        # Split into pairs
        pairs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
        
        decrypted = ""
        
        for pair in pairs:
            if len(pair) < 2:
                continue
                
            row1, col1 = PlayfairCipher.find_position(matrix, pair[0])
            row2, col2 = PlayfairCipher.find_position(matrix, pair[1])
            
            if row1 == row2:
                # Same row: shift left
                decrypted += matrix[row1][(col1 - 1) % 5]
                decrypted += matrix[row2][(col2 - 1) % 5]
            elif col1 == col2:
                # Same column: shift up
                decrypted += matrix[(row1 - 1) % 5][col1]
                decrypted += matrix[(row2 - 1) % 5][col2]
            else:
                # Rectangle: swap columns
                decrypted += matrix[row1][col2]
                decrypted += matrix[row2][col1]
        
        return decrypted


# Example usage
if __name__ == "__main__":
    plaintext = "Hello World"
    keyword = "SECRET"
    
    encrypted = PlayfairCipher.encrypt(plaintext, keyword)
    print(f"Plaintext: {plaintext}")
    print(f"Keyword: {keyword}")
    print(f"Encrypted: {encrypted}")
    
    decrypted = PlayfairCipher.decrypt(encrypted, keyword)
    print(f"Decrypted: {decrypted}")
