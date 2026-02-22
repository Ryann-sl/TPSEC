"""
Playfair Cipher Implementation (Simple Educational Version)
Uses a 5x5 Grid to encrypt pairs of letters (Digraphs).
"""

class PlayfairCipher:
    """A clean implementation of the Playfair Cipher for student study."""
    
    @staticmethod
    def prepare_key(keyword):
        """
        STEP 1: Create the 5x5 Key Matrix.
        1. Clean keyword (Upper, remove J).
        2. Fill matrix with unique keyword letters.
        3. Fill remaining cells with the rest of the alphabet.
        """
        keyword = keyword.upper().replace('J', 'I')
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ" # J is merged with I
        
        # Build list of unique characters starting with keyword
        unique_chars = []
        for char in (keyword + alphabet):
            if char not in unique_chars and char.isalpha():
                unique_chars.append(char)
        
        # Convert the flat list into a 5x5 matrix (list of lists)
        matrix = []
        for i in range(0, 25, 5):
            matrix.append(unique_chars[i:i+5])
        return matrix

    @staticmethod
    def find_position(matrix, char):
        """Find Row and Column index of a character in the grid."""
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == char:
                    return r, c
        return None, None

    @staticmethod
    def prepare_text(text):
        """
        STEP 2: Prepare the text into pairs (Digraphs).
        1. Replace J with I.
        2. Insert fillers (X, Z, Q) between repeat letters.
        3. Add a filler if total length is odd.
        """
        text = text.upper().replace('J', 'I').replace(' ', '')
        fillers = ['X', 'Z', 'Q']
        f_idx = 0
        
        pairs = []
        i = 0
        while i < len(text):
            char1 = text[i]
            
            # Case 1: Last character left alone (Add filler)
            if i == len(text) - 1:
                filler = fillers[f_idx % 3]
                if char1 == filler: filler = fillers[(f_idx + 1) % 3]
                pairs.append(char1 + filler)
                i += 1
            
            # Case 2: Next character is the same (Add filler in middle)
            elif char1 == text[i+1]:
                filler = fillers[f_idx % 3]
                if char1 == filler: filler = fillers[(f_idx + 1) % 3]
                pairs.append(char1 + filler)
                f_idx += 1
                i += 1
            
            # Case 3: Normal pair
            else:
                pairs.append(char1 + text[i+1])
                i += 2
        return pairs

    @staticmethod
    def encrypt(text, keyword):
        """
        STEP 3: Apply the 3 Rules of Playfair.
        """
        if not keyword:
            raise ValueError("Keyword is required")
        
        matrix = PlayfairCipher.prepare_key(keyword)
        pairs = PlayfairCipher.prepare_text(text)
        result = ""
        
        for p in pairs:
            r1, c1 = PlayfairCipher.find_position(matrix, p[0])
            r2, c2 = PlayfairCipher.find_position(matrix, p[1])
            
            # RULE 1: SAME ROW -> Shift Right
            if r1 == r2:
                result += matrix[r1][(c1 + 1) % 5]
                result += matrix[r2][(c2 + 1) % 5]
            
            # RULE 2: SAME COLUMN -> Shift Down
            elif c1 == c2:
                result += matrix[(r1 + 1) % 5][c1]
                result += matrix[(r2 + 1) % 5][c2]
                
            # RULE 3: RECTANGLE -> Swap Columns
            else:
                result += matrix[r1][c2]
                result += matrix[r2][c1]
        return result

    @staticmethod
    def decrypt(text, keyword):
        """
        STEP 4: Reverse the 3 Rules.
        """
        if not keyword:
            raise ValueError("Keyword is required")
        
        matrix = PlayfairCipher.prepare_key(keyword)
        # Split ciphertext into fixed digraphs (no extra prep needed)
        text = text.upper().replace(' ', '') # Ensure text is clean before pairing
        pairs = [text[i:i+2] for i in range(0, len(text), 2)]
        result = ""
        
        for p in pairs:
            if len(p) < 2: continue # Handle potential odd length ciphertext, though encrypt ensures even
            r1, c1 = PlayfairCipher.find_position(matrix, p[0])
            r2, c2 = PlayfairCipher.find_position(matrix, p[1])
            
            # RULE 1: SAME ROW -> Shift Left
            if r1 == r2:
                result += matrix[r1][(c1 - 1) % 5]
                result += matrix[r2][(c2 - 1) % 5]
            
            # RULE 2: SAME COLUMN -> Shift Up
            elif c1 == c2:
                result += matrix[(r1 - 1) % 5][c1]
                result += matrix[(r2 - 1) % 5][c2]
                
            # RULE 3: RECTANGLE -> Swap Columns
            else:
                result += matrix[r1][c2]
                result += matrix[r2][c1]
        return result

if __name__ == "__main__":
    key = "SECRET"
    msg = "HELLO"
    
    print(f"Plaintext: {msg}")
    print(f"Keyword: {key}")
    
    enc = PlayfairCipher.encrypt(msg, key)
    print(f"Playfair Encrypted: {enc}")
    
    dec = PlayfairCipher.decrypt(enc, key)
    print(f"Playfair Decrypted: {dec}")
