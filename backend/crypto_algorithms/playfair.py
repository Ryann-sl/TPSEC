class PlayfairCipher:
    """
    A pure Python implementation of the Playfair Cipher.
    No external libraries or APIs are used.
    Handles:
    - Matrix generation from a keyword
    - Digraph preparation (X insertion, padding)
    - Row, Column, and Rectangle encryption/decryption rules
    """

    def __init__(self, keyword: str):
        self.matrix = self.prepare_key(keyword)

    @staticmethod
    def prepare_key(keyword: str):
        """Builds a 5x5 matrix (I/J combined)."""
        # 1. Clean the keyword: uppercase, replace J with I, remove non-letters
        clean_key = ""
        for char in str(keyword).upper():
            if char == 'J': char = 'I'
            if 'A' <= char <= 'Z' and char not in clean_key:
                clean_key += char
        
        # 2. Fill with remaining alphabet (excluding J)
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
        full_chars = clean_key
        for char in alphabet:
            if char not in full_chars:
                full_chars += char
        
        # 3. Create 5x5 matrix
        return [list(full_chars[i:i+5]) for i in range(0, 25, 5)]

    def _get_pos(self, char: str):
        """Returns (row, col) of a character."""
        for r in range(5):
            for c in range(5):
                if self.matrix[r][c] == char:
                    return r, c
        return None

    def _prepare_text(self, text: str, for_encryption: bool = True):
        """Splits message into digraphs, adding 'X' or 'Q' where needed."""
        # Clean text
        msg = ""
        for char in str(text).upper():
            if char == 'J': char = 'I'
            if 'A' <= char <= 'Z':
                msg += char
        
        if not for_encryption:
            # For decryption, we assume it's already in digraphs
            # If length is odd, we pad with 'X' to avoid unpacking error
            if len(msg) % 2 != 0: msg += 'X'
            return [msg[i:i+2] for i in range(0, len(msg), 2)]

        prepared = []
        i = 0
        while i < len(msg):
            a = msg[i]
            if i + 1 < len(msg):
                b = msg[i+1]
                if a == b:
                    # If the letter is X, use Q as filler, otherwise use X
                    filler = 'Q' if a == 'X' else 'X'
                    prepared.append(a + filler)
                    i += 1
                else:
                    prepared.append(a + b)
                    i += 2
            else:
                # Padding for odd length
                filler = 'Q' if a == 'X' else 'X'
                prepared.append(a + filler)
                i += 1
        return prepared

    @staticmethod
    def encrypt(text: str, key: str):
        """Static method for encryption compatible with app.py"""
        instance = PlayfairCipher(key)
        pairs = instance._prepare_text(text, True)
        result = ""
        for a, b in pairs:
            pos1 = instance._get_pos(a)
            pos2 = instance._get_pos(b)
            
            if not pos1 or not pos2: continue
            
            r1, c1 = pos1
            r2, c2 = pos2

            if r1 == r2: # Same Row
                result += instance.matrix[r1][(c1 + 1) % 5] + instance.matrix[r2][(c2 + 1) % 5]
            elif c1 == c2: # Same Col
                result += instance.matrix[(r1 + 1) % 5][c1] + instance.matrix[(r2 + 1) % 5][c2]
            else: # Rectangle
                result += instance.matrix[r1][c2] + instance.matrix[r2][c1]
        return result

    @staticmethod
    def decrypt(text: str, key: str):
        """Static method for decryption compatible with app.py"""
        instance = PlayfairCipher(key)
        pairs = instance._prepare_text(text, False)
        result = ""
        for a, b in pairs:
            pos1 = instance._get_pos(a)
            pos2 = instance._get_pos(b)
            
            if not pos1 or not pos2: continue
            
            r1, c1 = pos1
            r2, c2 = pos2

            if r1 == r2: # Same Row
                result += instance.matrix[r1][(c1 - 1) % 5] + instance.matrix[r2][(c2 - 1) % 5]
            elif c1 == c2: # Same Col
                result += instance.matrix[(r1 - 1) % 5][c1] + instance.matrix[(r2 - 1) % 5][c2]
            else: # Rectangle
                result += instance.matrix[r1][c2] + instance.matrix[r2][c1]
        
        return result

# --- VULNERABILITY COVERAGE & TEST CASES ---
def run_demonstration():
    print("--- Playfair Pure Python (No APIs) ---")
    
    # 1. Standard Case
    print("\n[Case 1] Keyword: MONARCHY, Message: HELLO")
    enc = PlayfairCipher.encrypt("HELLO", "MONARCHY")
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {PlayfairCipher.decrypt(enc, 'MONARCHY')}")

    # 2. Repeated Letters (BALLOON) - Rule: Insert X
    print("\n[Case 2] Repeated Letters - BALLOON")
    enc2 = PlayfairCipher.encrypt("BALLOON", "SECRET")
    print(f"Encrypted: {enc2}")
    print(f"Decrypted: {PlayfairCipher.decrypt(enc2, 'SECRET')}")

if __name__ == "__main__":
    run_demonstration()
