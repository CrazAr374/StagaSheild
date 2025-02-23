from PIL import Image
import numpy as np
import zlib
import struct

def to_binary(data):
    """Convert data to binary format with compression."""
    try:
        if isinstance(data, str):
            compressed = zlib.compress(data.encode('utf-8'), level=6)
            binary = ''.join(format(b, '08b') for b in compressed)
            return binary
    except Exception:
        # If compression fails, fall back to direct binary conversion
        return ''.join(format(ord(c), '08b') for c in data)

def from_binary(binary_data):
    """Convert binary data back to string with decompression."""
    try:
        # Convert binary string to bytes
        data_bytes = int(binary_data, 2).to_bytes((len(binary_data) + 7) // 8, byteorder='big')
        # Try to decompress
        decompressed = zlib.decompress(data_bytes)
        return decompressed.decode('utf-8')
    except Exception:
        # If decompression fails, try direct conversion
        chunks = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        return ''.join(chr(int(chunk, 2)) for chunk in chunks if chunk)

def validate_image(image):
    """Validate and optimize image for steganography."""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Ensure image has sufficient size
    min_pixels = 100  # Minimum pixel requirement
    if image.size[0] * image.size[1] < min_pixels:
        raise ValueError("Image too small for steganography")
    
    return image

def get_image_capacity(image):
    """Calculate maximum message capacity."""
    # Use 1 bit per color channel (RGB)
    total_bits = image.size[0] * image.size[1] * 3
    # Reserve 32 bits for length header
    available_bits = total_bits - 32
    # Convert to bytes
    return available_bits // 8

def embed_message(image, message):
    """Embed message with improved reliability."""
    try:
        image = validate_image(image)
        img_array = np.array(image)
        
        # Convert message to binary
        binary_message = to_binary(message)
        message_length = len(binary_message)
        
        # Ensure message can fit
        max_capacity = get_image_capacity(image)
        if message_length > (max_capacity * 8):
            raise ValueError(f"Message too long. Maximum length is {max_capacity} bytes")
        
        # Use struct to pack length as 32-bit integer
        length_binary = format(message_length, '032b')
        binary_data = length_binary + binary_message
        
        # Create output array
        modified_array = img_array.copy()
        total_bits = len(binary_data)
        bits_embedded = 0
        
        # Embed data
        for h in range(img_array.shape[0]):
            for w in range(img_array.shape[1]):
                for c in range(3):  # RGB channels
                    if bits_embedded < total_bits:
                        # Clear LSB and embed one bit
                        pixel_value = modified_array[h, w, c]
                        new_pixel_value = (pixel_value & 0xFE) | int(binary_data[bits_embedded])
                        modified_array[h, w, c] = new_pixel_value
                        bits_embedded += 1
        
        return Image.fromarray(modified_array)
    
    except Exception as e:
        raise ValueError(f"Error embedding message: {str(e)}")

def extract_message(image):
    """Extract message with improved reliability."""
    try:
        image = validate_image(image)
        img_array = np.array(image)
        binary_data = ""
        
        # First extract the 32-bit length header
        for h in range(img_array.shape[0]):
            for w in range(img_array.shape[1]):
                for c in range(3):
                    binary_data += str(img_array[h, w, c] & 1)
                    if len(binary_data) == 32:
                        # Parse message length
                        message_length = int(binary_data, 2)
                        if message_length <= 0 or message_length > (get_image_capacity(image) * 8):
                            raise ValueError("Invalid message length detected")
                        
                        # Reset binary data for message content
                        binary_data = ""
                        
                        # Extract message content
                        remaining_pixels = ((message_length + 7) // 8) * 8  # Round up to nearest byte
                        for h2 in range(h, img_array.shape[0]):
                            for w2 in range(w if h2 == h else 0, img_array.shape[1]):
                                for c2 in range((c + 1) if h2 == h and w2 == w else 0, 3):
                                    if len(binary_data) < message_length:
                                        binary_data += str(img_array[h2, w2, c2] & 1)
                        
                        # Convert binary data to message
                        if len(binary_data) >= message_length:
                            return from_binary(binary_data[:message_length])
                        
        raise ValueError("No valid message found in image")
    
    except Exception as e:
        raise ValueError(f"Error extracting message: {str(e)}")

def can_embed(image, message):
    """Check if message can fit in image with compression estimate."""
    try:
        image = validate_image(image)
        # Estimate compressed size (typical compression ratio 1.5)
        estimated_size = len(message) / 1.5
        max_bytes = get_image_capacity(image)
        return estimated_size <= max_bytes
    except Exception:
        return False
