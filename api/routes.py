from flask import request, jsonify
from index import app  # Import the app instance
import requests 
import sys
import os

import logging 

logging.basicConfig(
    level=logging.DEBUG,  # Set the desired log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)
def create_user_uploads_directory():
    directory = 'user-uploads'
    if not os.path.exists(directory):
        os.makedirs(directory)


@app.route("/api/uploadFiles", methods=["POST"])
def upload_papers():
    logging.debug("come to upload fiels ")
    try:
        create_user_uploads_directory()

        uploaded_filenames = []
        for file in request.files.getlist("files"):
            logging.debug(file)
            logging.debug(file.name)
            if file and file.filename:
                # Use secure_filename to prevent malicious filenames
                filename = file.filename
                filepath = os.path.join("user-uploads", filename)
                file.save(filepath)
                uploaded_filenames.append(filename)

        return jsonify(uploaded_filenames), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/fetchFileNames", methods=['GET'])
def fetch_file_names():
    try:
        # Define the directory path where files are uploaded
        upload_directory = 'user-uploads'

        # Check if the directory exists
        if not os.path.exists(upload_directory):
            return jsonify([]), 200  # Return an empty list if the directory doesn't exist

        # List files in the directory and filter out subdirectories
        uploaded_files = [f for f in os.listdir(upload_directory) if os.path.isfile(os.path.join(upload_directory, f))]
        
        return jsonify(uploaded_files), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
