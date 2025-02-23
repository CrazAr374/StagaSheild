from PIL import Image
from steganalysis import analyze_image

def main():
    # Create a test image
    test_image = Image.new('RGB', (100, 100), color='white')
    
    # Analyze the image
    try:
        results = analyze_image(test_image)
        print("\n=== Test Analysis Results ===")
        print(f"LSB Distribution: {results['lsb_ratio']*100:.1f}%")
        print(f"Randomness Score: {results['randomness_score']*100:.1f}%")
        print(f"Hidden Content Probability: {results['probability']*100:.1f}%")
        print("\nAnalysis completed successfully!")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()
