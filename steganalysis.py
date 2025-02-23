import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive before importing pyplot
import matplotlib.pyplot as plt
import io
import base64

def analyze_image(image):
    """Analyze image for potential steganographic content."""
    img_array = np.array(image)
    
    # Calculate LSB patterns
    lsb_array = img_array & 1
    
    # Analyze LSB distribution
    lsb_ratio = np.mean(lsb_array)
    randomness_score = calculate_randomness(lsb_array)
    
    try:
        # Generate visualizations with explicit figure management
        modification_map = generate_modification_map(lsb_array)
        histogram_data = generate_histogram(img_array)
        
        return {
            'lsb_ratio': float(lsb_ratio),
            'randomness_score': float(randomness_score),
            'modification_map': modification_map,
            'histogram': histogram_data,
            'probability': calculate_probability(lsb_ratio, randomness_score)
        }
    except Exception as e:
        plt.close('all')  # Ensure all figures are closed
        raise e

def calculate_randomness(lsb_array):
    """Calculate randomness score of LSB distribution."""
    transitions = np.diff(lsb_array.flatten())
    transition_ratio = np.count_nonzero(transitions) / len(transitions)
    return transition_ratio

def generate_modification_map(lsb_array):
    """Generate a visual map of LSB modifications."""
    fig = plt.figure(figsize=(8, 8))
    try:
        plt.imshow(lsb_array.any(axis=2), cmap='hot')
        plt.colorbar(label='Modified Pixels')
        plt.title('LSB Modification Map')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    finally:
        plt.close(fig)

def generate_histogram(img_array):
    """Generate histogram of pixel values."""
    fig = plt.figure(figsize=(10, 4))
    try:
        colors = ['red', 'green', 'blue']
        for i, color in enumerate(colors):
            plt.hist(img_array[:,:,i].ravel(), bins=256, alpha=0.5, 
                    color=color, label=color.upper())
        
        plt.title('Color Channel Histogram')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.legend()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    finally:
        plt.close(fig)

def calculate_probability(lsb_ratio, randomness_score):
    """Calculate probability of hidden content."""
    # Simplified probability calculation
    # A more sophisticated model could be implemented here
    threshold = 0.5
    weighted_score = (lsb_ratio * 0.4 + randomness_score * 0.6)
    return min(weighted_score / threshold, 1.0)

def test_analysis(image_path):
    """Test function to analyze a single image."""
    try:
        # Load and analyze image
        image = Image.open(image_path)
        results = analyze_image(image)
        
        # Print results
        print("\n=== Steganography Analysis Results ===")
        print(f"LSB Distribution: {results['lsb_ratio']*100:.1f}%")
        print(f"Randomness Score: {results['randomness_score']*100:.1f}%")
        print(f"Hidden Content Probability: {results['probability']*100:.1f}%")
        
        # Save visualizations
        modification_map = base64.b64decode(results['modification_map'])
        histogram_data = base64.b64decode(results['histogram'])
        
        with open('modification_map.png', 'wb') as f:
            f.write(modification_map)
        with open('histogram.png', 'wb') as f:
            f.write(histogram_data)
        
        print("\nVisualization files saved:")
        print("- modification_map.png")
        print("- histogram.png")
        
        return True
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python steganalysis.py <image_path>")
        print("Example: python steganalysis.py test_image.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_analysis(image_path)
