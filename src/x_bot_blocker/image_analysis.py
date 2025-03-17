import os
import logging
import requests
import numpy as np
import cv2
from PIL import Image
import io
from typing import Dict, Optional, Tuple
from datetime import datetime
from config_manager import ConfigManager

class ImageAnalyzer:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.temp_dir = "temp_images"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Load configuration
        self.min_image_size = self.config.get('image_analysis.min_image_size', 100)
        self.max_image_size = self.config.get('image_analysis.max_image_size', 1000)
        self.face_detection_threshold = self.config.get('image_analysis.face_detection_threshold', 0.6)
        self.edge_detection_threshold = self.config.get('image_analysis.edge_detection_threshold', 100)
        
    def analyze_profile_image(self, image_url: str, username: str) -> Dict[str, any]:
        """
        Analyze a profile image for bot-like characteristics.
        Returns a dictionary with analysis results.
        """
        analysis = {
            'username': username,
            'image_url': image_url,
            'timestamp': datetime.now().isoformat(),
            'is_suspicious': False,
            'reasons': [],
            'metrics': {}
        }
        
        try:
            # Download and process image
            image = self._download_image(image_url)
            if image is None:
                analysis['reasons'].append("Failed to download image")
                return analysis
            
            # Convert to OpenCV format
            cv_image = self._pil_to_cv2(image)
            
            # Perform various analyses
            size_analysis = self._analyze_image_size(cv_image)
            face_analysis = self._analyze_face_detection(cv_image)
            edge_analysis = self._analyze_edge_detection(cv_image)
            color_analysis = self._analyze_color_distribution(cv_image)
            
            # Combine results
            analysis['metrics'].update({
                'size': size_analysis,
                'face_detection': face_analysis,
                'edge_detection': edge_analysis,
                'color_distribution': color_analysis
            })
            
            # Determine if image is suspicious
            if self._is_suspicious_image(analysis['metrics']):
                analysis['is_suspicious'] = True
                analysis['reasons'].extend(self._get_suspicious_reasons(analysis['metrics']))
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing image for {username}: {str(e)}")
            analysis['reasons'].append(f"Analysis error: {str(e)}")
            return analysis
            
    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Download image from URL and convert to PIL Image."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            self.logger.error(f"Error downloading image: {str(e)}")
            return None
            
    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format."""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
    def _analyze_image_size(self, image: np.ndarray) -> Dict[str, any]:
        """Analyze image dimensions."""
        height, width = image.shape[:2]
        return {
            'width': width,
            'height': height,
            'aspect_ratio': width / height if height > 0 else 0,
            'is_suspicious': width < self.min_image_size or width > self.max_image_size
        }
        
    def _analyze_face_detection(self, image: np.ndarray) -> Dict[str, any]:
        """Detect faces in the image."""
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        return {
            'face_count': len(faces),
            'is_suspicious': len(faces) == 0 or len(faces) > 1,
            'face_locations': faces.tolist() if len(faces) > 0 else []
        }
        
    def _analyze_edge_detection(self, image: np.ndarray) -> Dict[str, any]:
        """Analyze edge patterns in the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, self.edge_detection_threshold, self.edge_detection_threshold * 2)
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            'edge_density': float(edge_density),
            'is_suspicious': edge_density < 0.01 or edge_density > 0.5
        }
        
    def _analyze_color_distribution(self, image: np.ndarray) -> Dict[str, any]:
        """Analyze color distribution in the image."""
        colors = image.reshape(-1, 3)
        unique_colors = np.unique(colors, axis=0)
        color_count = len(unique_colors)
        
        return {
            'unique_colors': int(color_count),
            'is_suspicious': color_count < 10 or color_count > 1000
        }
        
    def _is_suspicious_image(self, metrics: Dict[str, any]) -> bool:
        """Determine if the image is suspicious based on all metrics."""
        suspicious_factors = [
            metrics['size']['is_suspicious'],
            metrics['face_detection']['is_suspicious'],
            metrics['edge_detection']['is_suspicious'],
            metrics['color_distribution']['is_suspicious']
        ]
        return any(suspicious_factors)
        
    def _get_suspicious_reasons(self, metrics: Dict[str, any]) -> list:
        """Get detailed reasons why the image is suspicious."""
        reasons = []
        
        if metrics['size']['is_suspicious']:
            reasons.append(f"Unusual image size: {metrics['size']['width']}x{metrics['size']['height']}")
            
        if metrics['face_detection']['is_suspicious']:
            reasons.append(f"Suspicious face count: {metrics['face_detection']['face_count']}")
            
        if metrics['edge_detection']['is_suspicious']:
            reasons.append(f"Unusual edge patterns: {metrics['edge_detection']['edge_density']:.2f}")
            
        if metrics['color_distribution']['is_suspicious']:
            reasons.append(f"Unusual color count: {metrics['color_distribution']['unique_colors']}")
            
        return reasons 