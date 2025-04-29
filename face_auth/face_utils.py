import cv2
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def detect_face_from_image(image_data):

    try:
       
        if isinstance(image_data, str) and image_data.startswith('data:image'):
           
            image_data = image_data.split(',')[1]
            image = Image.open(BytesIO(base64.b64decode(image_data)))
            image = np.array(image)
        else:
           
            image = np.array(Image.open(image_data))
            
       
        if len(image.shape) == 3 and image.shape[2] == 4: 
            image = image[:, :, :3]
            
       
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return None
            
        
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if not face_encodings:
            return None
            
      
        return face_encodings[0]
        
    except Exception as e:
        print(f"Error detecting face: {e}")
        return None

def capture_face_from_webcam():
 
    try:
       
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Could not open webcam")
            return None
            
        print("Capturing face... Look at the camera")
        
      
        ret, frame = cap.read()
        
     
        cap.release()
        
        if not ret:
            print("Failed to capture image")
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
       
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            print("No face detected")
            return None
            
      
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        if not face_encodings:
            print("Could not encode face")
            return None
            
     
        return face_encodings[0]
        
    except Exception as e:
        print(f"Error capturing face: {e}")
        return None

def verify_face(known_encoding, image_data, tolerance=0.6):

    try:
        
        face_encoding = detect_face_from_image(image_data)
        
        if face_encoding is None:
            return False
            
       
        matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=tolerance)
        
        return matches[0]
        
    except Exception as e:
        print(f"Error verifying face: {e}")
        return False