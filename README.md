# StegaShield

StegaShield is an advanced image steganography platform that allows you to securely conceal messages within images using cutting-edge steganography techniques. This project includes features such as embedding and extracting messages, batch processing, and image analysis for steganographic content.

## Features

- **Military-Grade Security**: Uses advanced LSB algorithms to ensure messages remain undetectable.
- **Real-time Analysis**: Provides instant steganalysis and detection capabilities.
- **Batch Processing**: Allows processing of multiple images simultaneously.
- **Advanced Analytics**: Offers detailed analysis reports and visualization of steganographic data.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/CrazAr374/StegaShield.git
    cd StegaShield
    ```

2. **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application:**
    ```bash
    python app.py
    ```

## Usage

1. **Launch the application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

2. **Embed a message:**
    - Go to the "Embed Message" tab.
    - Select an image and enter the secret message.
    - Click "Embed Message" to download the steganographic image.

3. **Extract a message:**
    - Go to the "Extract Message" tab.
    - Select an image with a hidden message.
    - Click "Extract Message" to view the hidden message.

4. **Batch Processing:**
    - Go to the "Batch Process" tab.
    - Select the mode (Embed or Extract) and upload multiple images.
    - For embedding, enter the secret message.
    - Click "Process Files" to download the results.

5. **Analyze an image:**
    - Go to the "Analyze Image" tab.
    - Select an image to analyze.
    - Click "Analyze Image" to view the steganographic analysis.

## API Endpoints

- **Embed Message:**
    ```http
    POST /embed
    ```
    - **Parameters:**
        - `image`: Image file (PNG, JPG, JPEG, BMP)
        - `message`: Secret message to embed

- **Extract Message:**
    ```http
    POST /extract
    ```
    - **Parameters:**
        - `image`: Image file (PNG, JPG, JPEG, BMP)

- **Batch Embed:**
    ```http
    POST /batch-embed
    ```
    - **Parameters:**
        - `images`: Multiple image files (PNG, JPG, JPEG, BMP)
        - `message`: Secret message to embed

- **Batch Extract:**
    ```http
    POST /batch-extract
    ```
    - **Parameters:**
        - `images`: Multiple image files (PNG, JPG, JPEG, BMP)

- **Analyze Image:**
    ```http
    POST /analyze
    ```
    - **Parameters:**
        - `image`: Image file (PNG, JPG, JPEG, BMP)


## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.
