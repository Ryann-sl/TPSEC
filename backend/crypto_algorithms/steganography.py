"""
Steganography Module - LSB (Least Significant Bit) Technique
This module implements image steganography using LSB technique to hide messages in images.
"""

from PIL import Image
import io
import base64
import binascii
import numpy as np

class Steganography:
    """
    Steganography class implementing LSB (Least Significant Bit) technique.
    
    How it works:
    1. Images are made of pixels, each pixel has RGB values (0-255)
    2. Each RGB value is 8 bits (binary representation)
    3. LSB technique replaces the least significant bit of each color channel with message bits
    4. This creates minimal visual changes to the image while hiding data
    
    Example:
    Original pixel: [R:255, G:128, B:64] 
    In binary: [11111111, 10000000, 01000000]
    Message bit: 1
    Modified pixel: [11111111, 10000001, 01000000] (LSB of Green changed)
    """
    
    def __init__(self):
        self.delimiter = "###END###"  # Message delimiter to mark end of hidden data
    
    def text_to_binary(self, text):
        """Convert text to binary string."""
        return ''.join(format(ord(char), '08b') for char in text)
    
    def binary_to_text(self, binary):
        """Convert binary string back to text."""
        try:
            text = ''
            for i in range(0, len(binary), 8):
                if i + 8 <= len(binary):
                    byte = binary[i:i+8]
                    text += chr(int(byte, 2))
            return text
        except:
            return ""
    
    def encode_message(self, image_path, message):
        """
        Hide a message in an image using LSB technique.
        
        Args:
            image_path: Path to the cover image
            message: Secret message to hide
            
        Returns:
            base64 encoded image with hidden message
        """
        try:
            # Open image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get image dimensions
            width, height = img.size
            
            # Add delimiter to message
            full_message = message + self.delimiter
            binary_message = self.text_to_binary(full_message)
            
            # Check if message fits in image
            max_bits = width * height * 3  # 3 color channels per pixel
            if len(binary_message) > max_bits:
                raise ValueError(f"Message too long. Max capacity: {max_bits // 8} characters")
            
            # Convert image to list of pixels
            pixels = list(img.getdata())
            
            # Embed message in LSBs
            message_index = 0
            modified_pixels = []
            
            for pixel in pixels:
                if message_index < len(binary_message):
                    r, g, b = pixel
                    modified_pixel = [r, g, b]
                    
                    # Modify each color channel
                    for channel in range(3):
                        if message_index < len(binary_message):
                            # Clear LSB and set it to message bit
                            modified_pixel[channel] = (modified_pixel[channel] & 0xFE) | int(binary_message[message_index])
                            message_index += 1
                        else:
                            break
                    
                    modified_pixels.append(tuple(modified_pixel))
                else:
                    # If message finished, append remaining pixels as they are
                    modified_pixels.append(pixel)
            
            # Create new image with modified pixels
            encoded_img = Image.new('RGB', img.size)
            encoded_img.putdata(modified_pixels)
            
            # Convert to base64 for web transmission
            buffer = io.BytesIO()
            encoded_img.save(buffer, format='PNG')
            encoded_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'success': True,
                'encoded_image': encoded_base64,
                'message_length': len(message),
                'image_size': f"{width}x{height}",
                'capacity_used': f"{len(binary_message)}/{max_bits} bits"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def decode_message(self, image_path):
        """
        Extract hidden message from an image.
        
        Args:
            image_path: Path to the image with hidden message
            
        Returns:
            Decoded message
        """
        try:
            # Open image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Extract LSBs
            binary_message = ''
            pixels = list(img.getdata())
            
            for pixel in pixels:
                r, g, b = pixel
                
                # Extract LSB from each color channel
                for channel in [r, g, b]:
                    lsb = channel & 1
                    binary_message += str(lsb)
                    
                    # Check for delimiter periodically
                    if len(binary_message) % 8 == 0:
                        try:
                            current_text = self.binary_to_text(binary_message)
                            if self.delimiter in current_text:
                                # Extract message before delimiter
                                message = current_text.split(self.delimiter)[0]
                                return {
                                    'success': True,
                                    'message': message,
                                    'bits_extracted': len(binary_message)
                                }
                        except:
                            continue
            
            # If no delimiter found, try to decode what we have
            try:
                message = self.binary_to_text(binary_message)
                return {
                    'success': True,
                    'message': message,
                    'bits_extracted': len(binary_message),
                    'note': 'No delimiter found, decoded all bits'
                }
            except:
                return {
                    'success': False,
                    'error': 'No hidden message found or message corrupted'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_image(self, image_path):
        """
        Analyze an image to check for hidden messages and show statistics.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Image analysis results
        """
        try:
            img = Image.open(image_path)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            total_pixels = width * height
            max_capacity = total_pixels * 3  # 3 bits per pixel (RGB)
            max_chars = max_capacity // 8
            
            # Check for potential hidden message
            img_array = np.array(img)
            flat_array = img_array.flatten()
            
            # Extract first few bits to check for patterns
            sample_bits = ''
            for i in range(min(100, len(flat_array))):
                sample_bits += str(flat_array[i] & 1)
            
            # Look for delimiter in sample
            has_delimiter = False
            try:
                sample_text = self.binary_to_text(sample_bits)
                if self.delimiter[:10] in sample_text:  # Check partial delimiter
                    has_delimiter = True
            except:
                pass
            
            return {
                'success': True,
                'image_info': {
                    'size': f"{width}x{height}",
                    'pixels': total_pixels,
                    'mode': img.mode
                },
                'capacity': {
                    'max_bits': max_capacity,
                    'max_characters': max_chars,
                    'used_percentage': 0
                },
                'analysis': {
                    'has_potential_message': has_delimiter,
                    'sample_bits': sample_bits[:50] + '...' if len(sample_bits) > 50 else sample_bits
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_technique_info(self):
        """
        Get information about LSB steganography technique.
        
        Returns:
            Educational information about the technique
        """
        return {
            'name': 'LSB (Least Significant Bit) Steganography',
            'description': 'Hides data in the least significant bits of image pixels',
            'how_it_works': [
                'Images consist of pixels with RGB color values (0-255)',
                'Each color value is represented by 8 bits in binary',
                'LSB technique replaces the least significant bit with message bits',
                'This creates minimal visual changes to the image',
                'Human eyes cannot detect these small changes'
            ],
            'advantages': [
                'Simple to implement',
                'Minimal visual distortion',
                'Works with most image formats',
                'Relatively high capacity'
            ],
            'disadvantages': [
                'Vulnerable to statistical analysis',
                'Can be detected with specialized tools',
                'Message is lost if image is compressed',
                'Not secure against determined attackers'
            ],
            'capacity_calculation': 'Image Width × Image Height × 3 bits = Total capacity',
            'example': {
                'image_size': '100x100 pixels',
                'total_pixels': '10,000',
                'max_capacity': '30,000 bits (3,750 characters)',
                'note': 'LSB uses 1 bit per color channel (R, G, B)'
            }
        }

# Global steganography instance
stego = Steganography()
