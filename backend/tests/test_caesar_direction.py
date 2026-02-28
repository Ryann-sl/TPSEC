import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

from crypto_algorithms.caesar import CaesarCipher

class TestCaesarDirection(unittest.TestCase):
    def test_encrypt_right(self):
        # A + 3 Right = D
        self.assertEqual(CaesarCipher.encrypt('ABC', 3, 'right'), 'DEF')
        # Z + 1 Right = A
        self.assertEqual(CaesarCipher.encrypt('Z', 1, 'right'), 'A')

    def test_encrypt_left(self):
        # A + 1 Left = Z
        self.assertEqual(CaesarCipher.encrypt('A', 1, 'left'), 'Z')
        # D + 3 Left = A
        self.assertEqual(CaesarCipher.encrypt('DEF', 3, 'left'), 'ABC')

    def test_decrypt_right(self):
        # Decrypt D (Shift 3 Right) = A
        self.assertEqual(CaesarCipher.decrypt('DEF', 3, 'right'), 'ABC')

    def test_decrypt_left(self):
        # Decrypt Z (Shift 1 Left) = A
        self.assertEqual(CaesarCipher.decrypt('Z', 1, 'left'), 'A')

    def test_mixed_case(self):
        self.assertEqual(CaesarCipher.encrypt('Hello', 3, 'right'), 'Khoor')
        self.assertEqual(CaesarCipher.decrypt('Khoor', 3, 'right'), 'Hello')

    def test_non_alpha(self):
        self.assertEqual(CaesarCipher.encrypt('A! B', 1, 'right'), 'B! C')

    def test_negative_shift_handling(self):
        # Even if user sends negative, we treat as absolute
        self.assertEqual(CaesarCipher.encrypt('ABC', -3, 'right'), 'DEF')

if __name__ == '__main__':
    unittest.main()
