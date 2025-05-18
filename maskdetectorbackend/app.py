from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
import tensorflow as tf
from flask_cors import CORS
import uuid
import base64
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging
import json
import sys



# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://192.168.49.2:30000/", "http://image-processing-backend:5000/","http://192.168.49.2:30001/"]}})
app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": [
        "http://localhost:3000",
        "http://192.168.49.2:30000",  # Add without trailing slash
        "http://192.168.49.2:30000/", # Keep with trailing slash
        "http://192.168.49.2:30001",
        "http://192.168.49.2:30001/",
        "http://image-processing-backend:5000",
        "http://image-processing-backend:5000/"
    ],
    "methods": ["GET", "POST", "OPTIONS"],  # Explicitly allow POST and OPTIONS
    "allow_headers": ["Content-Type", "Authorization"],  # Allow required headers
    "supports_credentials": True  # Optional, only if credentials are needed
}})


# Configure logging for JSON output
logger = logging.getLogger('image-processing-backend')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_record)

formatter = JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# MySQL configuration from environment variables
db_config = {
    'host': os.getenv('MYSQL_HOST', 'image-processing-mysql'),
    'user': os.getenv('MYSQL_USER', 'naval'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'image_processing'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        logger.info("Successfully connected to MySQL database")
        return connection
    except Error as e:
        logger.error(f"Failed to connect to MySQL: {str(e)}")
        return None

def preprocess_image(image_path, target_shape=(64, 64)):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized_img = cv2.resize(gray_img, target_shape, interpolation=cv2.INTER_AREA)
        normalized_img = resized_img / 255.0
        model_input = np.expand_dims(normalized_img, axis=(0, -1))
        logger.info(f"Preprocessed image: {image_path}")
        return model_input
    except Exception as e:
        logger.error(f"Error preprocessing image {image_path}: {str(e)}")
        raise

@app.route('/predict', methods=['POST'])
def predict():
    connection = None
    try:
        if 'image_name' not in request.files:
            logger.error("No image file provided in request")
            return jsonify({'status': 'error', 'message': 'No image file provided'}), 400

        file = request.files['image_name']
        if file.filename == '':
            logger.error("No file selected in request")
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400

        upload_dir = os.path.join(os.getcwd(), 'Uploads')
        output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        unique_id = uuid.uuid4().hex
        original_filename = f"original_{unique_id}_{file.filename}"
        processed_filename = f"output_{unique_id}_{file.filename}"
        original_path = os.path.join(upload_dir, original_filename)
        output_path = os.path.join(output_dir, processed_filename)

        file.save(original_path)
        logger.info(f"Saved original image: {original_path}")

        model_path = os.path.join(os.getcwd(), 'unet_model.h5')
        model = tf.keras.models.load_model(model_path)
        logger.info("Loaded U-Net model successfully")

        model_input = preprocess_image(original_path)
        prediction = model.predict(model_input, verbose=0)
        predicted_mask = prediction[0]
        predicted_mask = (predicted_mask * 255).astype(np.uint8).squeeze()

        cv2.imwrite(output_path, predicted_mask)
        logger.info(f"Saved predicted mask: {output_path}")

        with open(output_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        connection = get_db_connection()
        if connection is None:
            logger.error("Database connection failed during predict")
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        cursor = connection.cursor()
        query = """
        INSERT INTO process (original_filename, processed_filename, time, status)
        VALUES (%s, %s, %s, %s)
        """
        values = (original_filename, processed_filename, datetime.now(), 'success')
        cursor.execute(query, values)
        connection.commit()
        record_id = cursor.lastrowid
        logger.info(f"Inserted record into MySQL: record_id={record_id}, original_filename={original_filename}")

        cursor.close()

        return jsonify({
            'status': 'success',
            'record_id': record_id,
            'original_filename': original_filename,
            'output_filename': processed_filename,
            'image_base64': f'data:image/jpeg;base64,{encoded_image}'
        }), 200

    except Exception as e:
        if connection is None:
            connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = """
            INSERT INTO process (original_filename, processed_filename, time, status)
            VALUES (%s, %s, %s, %s)
            """
            values = (original_filename if 'original_filename' in locals() else 'unknown',
                      processed_filename if 'processed_filename' in locals() else 'unknown',
                      datetime.now(), 'failed')
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            logger.info("Logged error to MySQL database")

        logger.error(f"Error in predict endpoint: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.info("Closed MySQL connection")

@app.route('/result', methods=['GET'])
def result():
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            logger.error("Database connection failed during result endpoint")
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, original_filename, processed_filename, time, status FROM process"
        cursor.execute(query)
        records = cursor.fetchall()
        logger.info(f"Retrieved {len(records)} records from MySQL")

        cursor.close()
        return jsonify({
            'status': 'success',
            'records': records
        }), 200

    except Exception as e:
        logger.error(f"Error in result endpoint: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.info("Closed MySQL connection")

@app.route('/image/<int:id>', methods=['GET'])
def getImage(id):
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            logger.error("Database connection failed during getImage endpoint")
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        query = "SELECT original_filename, processed_filename FROM process WHERE id = %s"
        cursor.execute(query, (id,))
        record = cursor.fetchone()

        if not record:
            logger.warning(f"Record not found for id={id}")
            return jsonify({'status': 'error', 'message': 'Record not found'}), 404

        original_path = os.path.join(os.getcwd(), 'Uploads', record['original_filename'])
        processed_path = os.path.join(os.getcwd(), 'output', record['processed_filename'])

        if not os.path.exists(original_path) or not os.path.exists(processed_path):
            logger.error(f"Image files not found: original={original_path}, processed={processed_path}")
            return jsonify({'status': 'error', 'message': 'Image files not found'}), 404

        with open(original_path, 'rb') as orig_file:
            original_base64 = base64.b64encode(orig_file.read()).decode('utf-8')
        with open(processed_path, 'rb') as proc_file:
            processed_base64 = base64.b64encode(proc_file.read()).decode('utf-8')

        logger.info(f"Retrieved images for id={id}")
        cursor.close()
        return jsonify({
            'status': 'success',
            'original_image': f'data:image/jpeg;base64,{original_base64}',
            'processed_image': f'data:image/jpeg;base64,{processed_base64}',
            'original_filename': record['original_filename'],
            'processed_filename': record['processed_filename']
        }), 200

    except Exception as e:
        logger.error(f"Error in getImage endpoint: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.info("Closed MySQL connection")

@app.route('/test-db', methods=['GET'])
def test_db():
    connection = get_db_connection()
    if connection:
        logger.info("Successfully connected to MySQL via test-db endpoint")
        connection.close()
        return jsonify({'status': 'success', 'message': 'Connected to MySQL'})
    logger.error("Failed to connect to MySQL via test-db endpoint")
    return jsonify({'status': 'error', 'message': 'Failed to connect to MySQL'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5000)