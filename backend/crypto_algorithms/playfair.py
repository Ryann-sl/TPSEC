import re

class PlayfairCipher:
    ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

    @staticmethod
    def prepare_key(keyword: str):
        if not keyword or not keyword.strip():
            raise ValueError("Keyword is required")
        keyword = re.sub(r"[^A-Za-z]", "", keyword.upper()).replace("J", "I")
        unique_chars = []
        for ch in keyword + PlayfairCipher.ALPHABET:
            if ch.isalpha() and ch not in unique_chars:
                unique_chars.append(ch)
        matrix = [unique_chars[i:i + 5] for i in range(0, 25, 5)]
        return matrix

    @staticmethod
    def find_position(matrix, char: str):
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == char:
                    return r, c
        raise ValueError(f"Character '{char}' not found in Playfair matrix")

    @staticmethod
    def prepare_text(text: str, filler: str = "X"):
        if not text:
            return []
        filler = filler.upper()
        if filler == "J":
            filler = "I"
        text = re.sub(r"[^A-Za-z]", "", text.upper()).replace("J", "I")
        pairs = []
        i = 0
        while i < len(text):
            a = text[i]
            if i == len(text) - 1:
                b = filler if a != filler else "Z"
                pairs.append(a + b)
                break
            b = text[i + 1]
            if a == b:
                ins = filler if a != filler else "Z"
                pairs.append(a + ins)
                i += 1
            else:
                pairs.append(a + b)
                i += 2
        return pairs

    @staticmethod
    def encrypt(plaintext: str, keyword: str, filler: str = "X"):
        matrix = PlayfairCipher.prepare_key(keyword)
        pairs = PlayfairCipher.prepare_text(plaintext, filler=filler)
        result = []
        for p in pairs:
            r1, c1 = PlayfairCipher.find_position(matrix, p[0])
            r2, c2 = PlayfairCipher.find_position(matrix, p[1])
            if r1 == r2:
                result.append(matrix[r1][(c1 + 1) % 5])
                result.append(matrix[r2][(c2 + 1) % 5])
            elif c1 == c2:
                result.append(matrix[(r1 + 1) % 5][c1])
                result.append(matrix[(r2 + 1) % 5][c2])
            else:
                result.append(matrix[r1][c2])
                result.append(matrix[r2][c1])
        return "".join(result)

    @staticmethod
    def decrypt(ciphertext: str, keyword: str):
        matrix = PlayfairCipher.prepare_key(keyword)
        text = re.sub(r"[^A-Za-z]", "", ciphertext.upper()).replace("J", "I")
        if len(text) % 2 != 0:
            raise ValueError("Ciphertext length must be even.")
        
        pairs = [text[i:i + 2] for i in range(0, len(text), 2)]
        result = []
        for p in pairs:
            r1, c1 = PlayfairCipher.find_position(matrix, p[0])
            r2, c2 = PlayfairCipher.find_position(matrix, p[1])
            if r1 == r2:
                result.append(matrix[r1][(c1 - 1) % 5])
                result.append(matrix[r2][(c2 - 1) % 5])
            elif c1 == c2:
                result.append(matrix[(r1 - 1) % 5][c1])
                result.append(matrix[(r2 - 1) % 5][c2])
            else:
                result.append(matrix[r1][c2])
                result.append(matrix[r2][c1])
        
        decrypted = "".join(result)
        
        # Post-process to remove filler characters
        # Filler is 'X', but if 'X' was between two Identical chars, it's 'X' or 'Z'
        # This is a bit heuristic since standard Playfair doesn't guarantee lossless original text
        # But we'll try to remove 'X' if it's between two identical chars or at the end
        
        final_chars = []
        i = 0
        while i < len(decrypted):
            if i + 2 < len(decrypted) and decrypted[i] == decrypted[i+2] and (decrypted[i+1] == 'X' or decrypted[i+1] == 'Z'):
                final_chars.append(decrypted[i])
                i += 2
            else:
                final_chars.append(decrypted[i])
                i += 1
        
        # Remove trailing X or Z if added as padding
        res = "".join(final_chars)
        if len(res) > 1 and (res[-1] == 'X' or res[-1] == 'Z'):
            # Only remove if it was likely padding (i.e. to make it even)
            # In prepare_text, we always make it even.
            # However, we don't know the original length here.
            # We'll just remove the trailing filler as is common in educational tools.
            res = res[:-1]
            
        return res

if __name__ == "__main__":
    key = "SECRET"
    msg = "HELLO WORLD"
    enc = PlayfairCipher.encrypt(msg, key)
    dec = PlayfairCipher.decrypt(enc, key)
    print("Encrypted:", enc)
    print("Decrypted:", dec)
