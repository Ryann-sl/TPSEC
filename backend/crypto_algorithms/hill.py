"""
Hill Cipher - Clean & Understandable Implementation
"""

class HillCipher:
    @staticmethod
    def get_mod_inverse(a, m=26):
        """Find modular inverse of a mod m using brute-force search."""
        a %= m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return None

    @staticmethod
    def get_determinant(matrix):
        """Recursive determinant calculation for any square matrix."""
        n = len(matrix)
        if n == 0: return 1
        if n == 1: return matrix[0][0]
        if n == 2: return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
        
        det = 0
        for j in range(n):
            minor = [row[:j] + row[j+1:] for row in matrix[1:]]
            det += ((-1)**j) * matrix[0][j] * HillCipher.get_determinant(minor)
        return det

    @staticmethod
    def get_adjugate_matrix(matrix):
        """Calculate the adjugate matrix (transpose of the cofactor matrix)."""
        n = len(matrix)
        if n == 2:
            return [[matrix[1][1], -matrix[0][1]], [-matrix[1][0], matrix[0][0]]]
            
        adj = []
        for i in range(n):
            row = []
            for j in range(n):
                minor = [r[:j] + r[j+1:] for r in (matrix[:i] + matrix[i+1:])]
                row.append(((-1)**(i+j)) * HillCipher.get_determinant(minor))
            adj.append(row)
        return [[adj[j][i] for j in range(n)] for i in range(n)]

    @staticmethod
    def text_to_numbers(text):
        """Convert uppercase letters A-Z to numbers 0-25."""
        return [ord(c.upper()) - ord('A') for c in text if c.isalpha()]

    @staticmethod
    def numbers_to_text(numbers):
        """Convert numbers 0-25 back to uppercase A-Z."""
        return "".join(chr((n % 26) + ord('A')) for n in numbers)

    @staticmethod
    def prepare_key_matrix(key, size=None):
        """ Standardize key into an NxN matrix. Infers size if not specified. """
        if not key: raise ValueError("Empty Key: No encryption possible.")

        # 1. Handle Matrix Input
        if isinstance(key, list) and len(key) > 0 and isinstance(key[0], list):
            if len(key) != len(key[0]): raise ValueError("Key must be a square matrix.")
            return key
            
        # 2. Extract Numbers from String or Flat List
        nums = []
        if isinstance(key, str):
            import re
            # Try to find integers first (handles "3 3 2 5" or "3,3,2,5")
            nums = [int(n) for n in re.findall(r'-?\d+', key)]
            if not nums: # If no digits, treat as alphabetic string (e.g., "HILL")
                nums = HillCipher.text_to_numbers(key)
        elif isinstance(key, list):
            nums = [int(n) for n in key] # Convert flat list to integers

        if not nums: raise ValueError("Invalid Key: No numeric values found.")

        # 3. Infer Matrix Size (n) if not provided
        if size is None:
            size = int(len(nums)**0.5)
            if size < 2: size = 2 # Smallest meaningful block

        # 4. Pad with 0s if needed, then reshape
        nums += [0] * (size*size - len(nums))
        return [nums[i*size : (i+1)*size] for i in range(size)]

    @staticmethod
    def encrypt(text, key, size=None):
        """Encrypt text using Hill Cipher. size is optional (inferred from key length)."""
        K = HillCipher.prepare_key_matrix(key, size)
        n = len(K)
        
        # Check Key Validity
        det = HillCipher.get_determinant(K) % 26
        if HillCipher.get_mod_inverse(det) is None:
            raise ValueError(f"Invalid Key: Determinant {det} is not coprime with 26.")

        # Convert and Pad Plaintext
        p_nums = HillCipher.text_to_numbers(text)
        while len(p_nums) % n != 0: p_nums.append(ord('X') - ord('A'))
        
        # Encryption: Cipher = Matrix * Vector mod 26
        c_nums = []
        for i in range(0, len(p_nums), n):
            block = p_nums[i : i+n]
            for r in range(n):
                c_nums.append(sum(K[r][c] * block[c] for c in range(n)) % 26)
        
        return HillCipher.numbers_to_text(c_nums)

    @staticmethod
    def decrypt(text, key, size=None):
        """Decrypt text using Hill Cipher. size is optional (inferred from key length)."""
        K = HillCipher.prepare_key_matrix(key, size)
        n = len(K)
        
        # Check Key Validity and find Inverse Matrix
        det = HillCipher.get_determinant(K) % 26
        det_inv = HillCipher.get_mod_inverse(det)
        if det_inv is None:
            raise ValueError("Invalid Key: Matrix is not invertible mod 26.")

        adj = HillCipher.get_adjugate_matrix(K)
        K_inv = [[(val * det_inv) % 26 for val in row] for row in adj]
        
        # Decryption: Plain = Matrix_Inverse * Vector mod 26
        c_nums = HillCipher.text_to_numbers(text)
        p_nums = []
        for i in range(0, len(c_nums), n):
            block = c_nums[i : i+n]
            for r in range(n):
                p_nums.append(sum(K_inv[r][c] * block[c] for c in range(n)) % 26)
        
        return HillCipher.numbers_to_text(p_nums)

    @staticmethod
    def solve_key(plaintext, ciphertext, size):
        """Attack: Recover the key matrix K given enough known plaintext/ciphertext pairs."""
        p_nums = HillCipher.text_to_numbers(plaintext)
        c_nums = HillCipher.text_to_numbers(ciphertext)
        
        if len(p_nums) < size*size: raise ValueError(f"Need at least {size*size} letters to solve.")

        # Fill P and C matrices (columns are blocks)
        P, C = [[0]*size for _ in range(size)], [[0]*size for _ in range(size)]
        for col in range(size):
            for row in range(size):
                P[row][col] = p_nums[col*size + row]
                C[row][col] = c_nums[col*size + row]

        # K = C * P_Inverse
        det_p = HillCipher.get_determinant(P) % 26
        inv_det_p = HillCipher.get_mod_inverse(det_p)
        if inv_det_p is None: return "Cannot solve: Plaintext matrix is not invertible mod 26."

        adj_p = HillCipher.get_adjugate_matrix(P)
        P_inv = [[(v * inv_det_p) % 26 for v in r] for r in adj_p]
        
        K = [[sum(C[r][i] * P_inv[i][c] for i in range(size)) % 26 for c in range(size)] for r in range(size)]
        return K

if __name__ == "__main__":
    # Quick Check with "HILL"
    try:
        k = "HILL"
        e = HillCipher.encrypt("HELP", k)
        print(f"Key 'HILL' -> Encrypted 'HELP': {e}") # Expected: DRPA
        print(f"Decrypted: {HillCipher.decrypt(e, k)}")
    except Exception as ex:
        print(f"Error: {ex}")
