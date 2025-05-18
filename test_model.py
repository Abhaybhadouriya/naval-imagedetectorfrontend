import os
import numpy as np
import tensorflow as tf
from PIL import Image


def preprocess_image(image_path, target_size=(64, 64)):
    """Preprocess image for model input."""
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img = img.resize(target_size)
    img_array = np.array(img) / 255.0  # Normalize
    img_array = img_array.reshape(1, target_size[0], target_size[1], 1)  # Add batch and channel
    return img_array

def test_model():
    """Test the model with an image from the images folder."""
    model_path = 'model.h5'
    image_folder = 'images'
    image_file = '000000_1.jpg'  # Replace with your image filename

    # Check if model and image exist
    if not os.path.exists(model_path):
        print(f"Error: Model file {model_path} not found")
        return False
    image_path = os.path.join(image_folder, image_file)
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} not found")
        return False

    # Load model
    try:
        model = tf.keras.models.load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

    # Preprocess image and predict
    try:
        img_array = preprocess_image(image_path)
        prediction = model.predict(img_array)
        print(f"Prediction: {prediction}")
        # Validate prediction (adjust based on your model's output, e.g., binary classification)
        if prediction.shape[0] == 1 and len(prediction[0]) == 1:  # Assuming binary output
            print("Model test passed")
            return True
        else:
            print("Unexpected prediction shape")
            return False
    except Exception as e:
        print(f"Error during prediction: {e}")
        return False

if __name__ == "__main__":
    if test_model():
        print("Test successful")
        exit(0)
    else:
        print("Test failed")
        exit(1)