import unittest
import os
import sys
from PIL import Image
import numpy as np
import io
import base64

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_algorithms.steganography import Steganography

class TestSteganography(unittest.TestCase):
    def setUp(self):
        self.stego = Steganography()
        self.test_img_path = 'test_image.png'
        # Create a small dummy image for testing
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_img_path)

    def tearDown(self):
        if os.path.exists(self.test_img_path):
            os.remove(self.test_img_path)

    def test_encode_decode_integrity(self):
        message = "Secret Message!"
        result = self.stego.encode_message(self.test_img_path, message)
        
        self.assertTrue(result['success'])
        
        # Verify image dimensions are preserved
        img_data = base64.b64decode(result['encoded_image'])
        img = Image.open(io.BytesIO(img_data))
        self.assertEqual(img.size, (100, 100))
        
        # Decode and verify message
        # Save encoded image to temporary file for decoding
        temp_encoded = 'temp_encoded.png'
        img.save(temp_encoded)
        
        decode_result = self.stego.decode_message(temp_encoded)
        self.assertTrue(decode_result['success'])
        self.assertEqual(decode_result['message'], message)
        
        os.remove(temp_encoded)

    def test_truncation_fix(self):
        # This test specifically checks if the entire image data is present
        message = "A" # Very short message
        result = self.stego.encode_message(self.test_img_path, message)
        
        img_data = base64.b64decode(result['encoded_image'])
        img = Image.open(io.BytesIO(img_data))
        
        # putdata should not have failed, and image should have 10000 pixels
        pixels = list(img.getdata())
        self.assertEqual(len(pixels), 100 * 100)

if __name__ == '__main__':
    unittest.main()
