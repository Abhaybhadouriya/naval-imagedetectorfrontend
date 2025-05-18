import tensorflow as tf
import numpy as np
from PIL import Image
import os

def load_and_preprocess_image(image_path):
    img = Image.open(image_path).resize((128, 128))  # Adjusted for U-Net model
    img_array = np.array(img) / 255.0  # Normalize
    return np.expand_dims(img_array, axis=0)

def test_model():
    # Load model
    model = tf.keras.models.load_model('maskdetectorbackend/unet_model.h5')
    
    # Directory containing test images
    image_dir = 'maskdetectorbackend/images'
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Directory {image_dir} not found")
    
    # Test each image
    for image_file in os.listdir(image_dir):
        if image_file.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_dir, image_file)
            try:
                img_data = load_and_preprocess_image(image_path)
                prediction = model.predict(img_data)
                print(f"Prediction for {image_file}: {prediction}")
            except Exception as e:
                print(f"Error processing {image_file}: {str(e)}")

if __name__ == "__main__":
    test_model()