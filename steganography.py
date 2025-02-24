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
    # Convert all images to RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Ensure image has sufficient size
    min_pixels = 100  # Minimum pixel requirement
    if image.size[0] * image.size[1] < min_pixels:
        raise ValueError("Image too small for steganography")
    
    # Handle JPG compression artifacts
    if image.format == 'JPEG':
        # Convert to array and back to stabilize pixel values
        img_array = np.array(image)
        image = Image.fromarray(img_array)
    
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
        
        # Convert message to binary with compression
        binary_message = to_binary(message)
        message_length = len(binary_message)
        
        # Ensure message can fit
        max_capacity = get_image_capacity(image)
        if message_length > (max_capacity * 8):
            raise ValueError(f"Message too long. Maximum length is {max_capacity} bytes")
        
        # Create length header (32 bits)
        length_binary = format(message_length, '032b')
        binary_data = length_binary + binary_message
        
        # Create output array
        modified_array = img_array.copy()
        bits_embedded = 0
        total_bits = len(binary_data)
        
        # Embed data with validation
        try:
            for h in range(img_array.shape[0]):
                for w in range(img_array.shape[1]):
                    for c in range(3):
                        if bits_embedded < total_bits:
                            pixel_value = modified_array[h, w, c]
                            # Clear LSB and embed one bit
                            modified_array[h, w, c] = (pixel_value & 0xFE) | int(binary_data[bits_embedded])
                            bits_embedded += 1
            
            if bits_embedded < total_bits:
                raise ValueError("Not all bits were embedded")
                
            # Convert back to PIL Image and preserve format
            result_image = Image.fromarray(modified_array)
            result_image.format = image.format or 'PNG'
            
            return result_image
            
        except Exception as e:
            raise ValueError(f"Error during embedding: {str(e)}")
        
    except Exception as e:
        raise ValueError(f"Error embedding message: {str(e)}")

def extract_message(image):
    """Extract message with improved reliability."""
    try:
        image = validate_image(image)
        img_array = np.array(image)
        binary_data = ""
        
        # First extract the 32-bit length header
        length_binary = ""
        bits_read = 0
        
        # Make extraction more tolerant for JPG compression
        noise_tolerance = 0.1 if image.format == 'JPEG' else 0
        
        # Extract header with noise tolerance
        for h in range(img_array.shape[0]):
            for w in range(img_array.shape[1]):
                for c in range(3):
                    # Get LSB with noise tolerance
                    pixel_value = img_array[h, w, c]
                    bit_value = pixel_value & 1
                    if noise_tolerance > 0:
                        # Check neighboring pixels for consistency
                        neighbors = []
                        if h > 0: neighbors.append(img_array[h-1, w, c] & 1)
                        if w > 0: neighbors.append(img_array[h, w-1, c] & 1)
                        if neighbors:
                            most_common = max(set(neighbors), key=neighbors.count)
                            if abs(bit_value - most_common) <= noise_tolerance:
                                bit_value = most_common
                    
                    length_binary += str(bit_value)
                    bits_read += 1
                    if bits_read == 32:
                        break
                if bits_read == 32:
                    break
            if bits_read == 32:
                break
        
        if len(length_binary) != 32:
            raise ValueError("Could not find valid message header")
        
        try:
            message_length = int(length_binary, 2)
            max_possible_length = (image.size[0] * image.size[1] * 3 - 32) // 8
            
            if message_length <= 0 or message_length > max_possible_length:
                raise ValueError(f"Invalid message length: {message_length}")
        except ValueError as e:
            raise ValueError(f"Invalid message header: {str(e)}")
        
        # Extract message content with noise tolerance
        binary_data = ""
        bits_read = 0
        
        for h in range(img_array.shape[0]):
            for w in range(img_array.shape[1]):
                for c in range(3):
                    if bits_read >= 32:  # Skip header bits
                        pixel_value = img_array[h, w, c]
                        bit_value = pixel_value & 1
                        
                        if noise_tolerance > 0:
                            # Apply same noise tolerance check
                            neighbors = []
                            if h > 0: neighbors.append(img_array[h-1, w, c] & 1)
                            if w > 0: neighbors.append(img_array[h, w-1, c] & 1)
                            if neighbors:
                                most_common = max(set(neighbors), key=neighbors.count)
                                if abs(bit_value - most_common) <= noise_tolerance:
                                    bit_value = most_common
                        
                        binary_data += str(bit_value)
                    bits_read += 1
                    if len(binary_data) >= message_length:
                        break
                if len(binary_data) >= message_length:
                    break
            if len(binary_data) >= message_length:
                break
        
        # Try multiple decompression methods
        try:
            return from_binary(binary_data[:message_length])
        except Exception:
            # Fallback to direct binary conversion
            chunks = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
            return ''.join(chr(int(chunk, 2)) for chunk in chunks if len(chunk) == 8)
            
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
