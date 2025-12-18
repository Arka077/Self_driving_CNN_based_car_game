import numpy as np
from tensorflow import keras
import cv2
import os


class ModelPredictor:
    """Handles model loading, image preprocessing, and prediction"""
    
    def __init__(self, model_path='best_model.h5'):
        """Load the trained model"""
        self.model = keras.models.load_model(model_path)
        self.frame_count = 0
        
        # Action mapping
        self.action_map = {
            0: 'SWIPE_LEFT',
            1: 'CENTER',
            2: 'SWIPE_RIGHT'
        }
        self.reverse_action_map = {v: k for k, v in self.action_map.items()}
        
        # Create game_preds directory structure
        self.preds_dir = 'game_preds'
        self.action_dirs = {
            'SWIPE_LEFT': os.path.join(self.preds_dir, 'left'),
            'CENTER': os.path.join(self.preds_dir, 'no_action'),
            'SWIPE_RIGHT': os.path.join(self.preds_dir, 'right')
        }
        
        # Create directories if they don't exist
        for action, path in self.action_dirs.items():
            os.makedirs(path, exist_ok=True)
    
    def preprocess_image(self, img):
        """
        Preprocess image for model prediction
        EXACT SAME PIPELINE AS TRAINING (car.ipynb):
        Input: RGB image from pygame surface or cv2.cvtColor(cv2.imread(...), cv2.COLOR_BGR2RGB)
        Output: YUV, blurred, 200x400, normalized [0-1]
        
        ✅ MATCHES TRAINING: img_preprocess expects RGB input!
        """
        # Step 1: RGB → YUV (training: cv2.cvtColor(img, cv2.COLOR_RGB2YUV))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
        
        # Step 2: Gaussian Blur (training: cv2.GaussianBlur(img, (3, 3), 0))
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # Step 3: Resize to 200x400 (training: cv2.resize(img, (200, 400)))
        img = cv2.resize(img, (200, 400))
        
        # Step 4: Normalize to 0-1 (training: img/255)
        img = img / 255.0
        
        return img
    
    def predict(self, frame):
        """
        Make prediction on a frame 
        Input: BGR frame from pygame surface or cv2
        Output: Tuple of (action_string, confidence, all_probabilities)
        """
        try:
            # Preprocess the image
            processed_img = self.preprocess_image(frame)
            
            # Add batch dimension
            input_data = np.expand_dims(processed_img, axis=0)
            
            # Make prediction
            predictions = self.model.predict(input_data, verbose=0)
            
            # Get action with highest confidence
            action_index = np.argmax(predictions[0])
            confidence = predictions[0][action_index]
            
            # Map index to action
            action = self.action_map[action_index]
            
            
            return action, float(confidence), predictions[0]
        
        except Exception as e:
            print(f"Error in prediction: {e}")
            return 'CENTER', 0.0, [0.0, 1.0, 0.0]
    
    def get_action_name(self, action_index):
        """Convert action index to action name"""
        return self.action_map.get(action_index, 'CENTER')
