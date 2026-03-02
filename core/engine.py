import os
import cv2
import pytesseract
import numpy as np
from PIL import Image

class OCREngine:
    def __init__(self, tesseract_path=None, tessdata_dir=None):
        """
        Initialize the OCR Engine with Tesseract configuration.
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.tessdata_dir = tessdata_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tessdata')
        
        # Ensure TESSDATA_PREFIX is set for the environment if provided
        if tessdata_dir:
            os.environ['TESSDATA_PREFIX'] = tessdata_dir

    def preprocess_image(self, image_path):
        """
        Comprehensive image preprocessing for enhanced OCR accuracy.
        Applies grayscale conversion, denoising, and adaptive thresholding.
        """
        # Load image via OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")

        # Convert to grayscale for better contrast analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Remove electronic noise while preserving edges
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Adaptive thresholding to handle complex lighting conditions
        processed = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Generate a path for the temporary processed image
        base, ext = os.path.splitext(image_path)
        processed_path = f"{base}_proc{ext}"
        cv2.imwrite(processed_path, processed)
        
        return processed_path

    def extract_text(self, image_path, psm=3):
        """
        Performs OCR extraction on the provided image.
        Uses optimized Tesseract configuration.
        """
        try:
            # Preprocess the image first
            proc_path = self.preprocess_image(image_path)
            
            # Open processed image with PIL for Tesseract compatibility
            with Image.open(proc_path) as img:
                # Optimized config for better accuracy
                config = f'--tessdata-dir "{self.tessdata_dir}" --psm {psm}'
                text = pytesseract.image_to_string(img, config=config)
            
            # Cleanup temporary processed file
            if os.path.exists(proc_path):
                os.remove(proc_path)
                
            return text.strip() if text else ""
            
        except Exception as e:
            # Cleanup on failure if processor path exists
            if 'proc_path' in locals() and os.path.exists(proc_path):
                os.remove(proc_path)
            raise RuntimeError(f"OCR Extraction failed: {str(e)}")
