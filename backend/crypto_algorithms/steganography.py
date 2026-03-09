"""
Steganography Module - Multi-Media Carriers (Image, Audio, Video)
This module implements steganography using LSB technique for different media types.
"""

import io
import base64
import numpy as np
import os
from PIL import Image
import wave

class BaseSteganography:
    """Base class for steganography implementations"""
    def __init__(self):
        self.delimiter = "###END###"

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
        except Exception:
            return ""

    def extract_bits(self, bits_iterator):
        """Helper to extract message from a bit iterator effectively"""
        binary_char = ""
        decoded_text = ""
        for bit in bits_iterator:
            binary_char += str(bit)
            if len(binary_char) == 8:
                try:
                    char = chr(int(binary_char, 2))
                    decoded_text += char
                    binary_char = ""
                    if self.delimiter in decoded_text:
                        return {'success': True, 'message': decoded_text.split(self.delimiter)[0]}
                except Exception:
                    # If a byte cannot be converted to a character, reset and continue
                    # This handles cases where random bits might form invalid characters
                    binary_char = ""
                    continue
        return {'success': False, 'error': 'No hidden message found. This file does not appear to contain an encrypted secret.'}

class ImageSteganography(BaseSteganography):
    """Image steganography using LSB technique"""
    
    def encode_message(self, image_path, message):
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            full_message = message + self.delimiter
            binary_message = self.text_to_binary(full_message)
            
            max_bits = width * height * 3
            if len(binary_message) > max_bits:
                return {'success': False, 'error': f"Message too long. Max capacity: {max_bits // 8} characters"}
            
            pixels = np.array(img)
            flat_pixels = pixels.flatten()
            
            for i in range(len(binary_message)):
                flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(binary_message[i])
            
            encoded_pixels = flat_pixels.reshape(pixels.shape)
            encoded_img = Image.fromarray(encoded_pixels.astype('uint8'), 'RGB')
            
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
            return {'success': False, 'error': str(e)}

    def decode_message(self, image_path):
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            pixels = np.array(img).flatten()
            
            def bits_gen():
                for p in pixels:
                    yield p & 1
            
            return self.extract_bits(bits_gen())
        except Exception as e:
            return {'success': False, 'error': str(e)}

class AudioSteganography(BaseSteganography):
    """Audio steganography using LSB technique (WAV files)"""
    
    def encode_message(self, audio_path, message):
        try:
            audio = wave.open(audio_path, mode='rb')
            params = audio.getparams()
            frames = bytearray(list(audio.readframes(audio.getnframes())))
            audio.close()

            full_message = message + self.delimiter
            binary_message = self.text_to_binary(full_message)

            if len(binary_message) > len(frames):
                return {'success': False, 'error': "Message too long for this audio file"}

            for i in range(len(binary_message)):
                frames[i] = (frames[i] & 254) | int(binary_message[i])

            # Save to temporary buffer
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as fd:
                fd.setparams(params)
                fd.writeframes(frames)
            
            encoded_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'success': True,
                'encoded_audio': encoded_base64,
                'message_length': len(message),
                'capacity_used': f"{len(binary_message)}/{len(frames)} bits"
            }
        except wave.Error as e:
            return {'success': False, 'error': f"Audio format error: {str(e)}. Please use an uncompressed .wav file."}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def decode_message(self, audio_path):
        try:
            audio = wave.open(audio_path, mode='rb')
            frames = audio.readframes(audio.getnframes())
            audio.close()

            def bits_gen():
                for b in frames:
                    yield b & 1
            
            return self.extract_bits(bits_gen())
        except wave.Error as e:
            return {'success': False, 'error': f"Audio format error: {str(e)}. Please use an uncompressed .wav file."}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class VideoSteganography(BaseSteganography):
    """Video steganography using frame-based LSB technique"""
    
    def encode_message(self, video_path, message):
        tmp_path = None # Initialize tmp_path for cleanup in case of early error
        try:
            import cv2
            import tempfile
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {'success': False, 'error': "Could not open video file"}

            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
            
            full_message = message + self.delimiter
            binary_message = self.text_to_binary(full_message)
            max_bits = width * height * 3 # Actually more, but we'll cap it for safety
            
            # Create a temporary output file
            fd, tmp_path = tempfile.mkstemp(suffix='.avi')
            os.close(fd) # Close handle so OpenCV can use it

            # Lossless Huffman codec (common in OpenCV)
            fourcc = cv2.VideoWriter_fourcc(*'HFYU')
            out = cv2.VideoWriter(tmp_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                # Fallback to MJPG (not lossless but often works) if HFYU fails
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter(tmp_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                if os.path.exists(tmp_path): os.unlink(tmp_path)
                return {'success': False, 'error': "Could not initialize video writer with available codecs."}

            message_index = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if message_index < len(binary_message):
                    # Encode bits into this frame
                    flat_frame = frame.flatten()
                    for i in range(len(flat_frame)):
                        if message_index < len(binary_message):
                            flat_frame[i] = (flat_frame[i] & 254) | int(binary_message[message_index])
                            message_index += 1
                        else:
                            break
                    frame = flat_frame.reshape(frame.shape)
                
                out.write(frame)
            
            cap.release()
            out.release()

            if message_index < len(binary_message):
                if os.path.exists(tmp_path): os.unlink(tmp_path)
                return {'success': False, 'error': f"Video too short. Only {message_index // 8} characters could fit."}

            with open(tmp_path, 'rb') as f:
                encoded_base64 = base64.b64encode(f.read()).decode()
            
            os.unlink(tmp_path)

            return {
                'success': True,
                'encoded_video': encoded_base64,
                'message_length': len(message)
            }
        except Exception as e:
            if tmp_path and os.path.exists(tmp_path): os.unlink(tmp_path)
            return {'success': False, 'error': str(e)}

    def decode_message(self, video_path):
        cap = None # Initialize cap for cleanup
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {'success': False, 'error': "Could not open video file for decoding"}
            
            def bits_gen():
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    for b in frame.flatten():
                        yield b & 1
            
            result = self.extract_bits(bits_gen())
            cap.release()
            return result
        except Exception as e:
            if cap: cap.release()
            return {'success': False, 'error': str(e)}

# Global instances
img_stego = ImageSteganography()
audio_stego = AudioSteganography()
video_stego = VideoSteganography()

def get_technique_info():
    return {
        'types': ['Image', 'Audio', 'Video'],
        'technique': 'LSB (Least Significant Bit)',
        'description': 'Hides data in the least significant bits of media data.'
    }
