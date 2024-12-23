import requests;
import base64;
import io;
import os;

from flask import Flask, request, jsonify, send_file;
from rembg import remove;
import logging;
from utils.authenticate import Authenticate;
from config import config;

app = Flask(__name__);

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Allowed image extensions and their corresponding MIME types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"};
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"};

# Maximum allowed file size (in bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024;  # 5 MB

# Get image data
def get_image_data(image_data: str, input_type: str):
    if (input_type == "file"):
        image_data = image_data.read();
    elif (input_type == "base64"):
        image_data = base64.b64decode(image_data);
    elif (input_type == "url"):
        image_data = requests.get(image_data, allow_redirects=True).content;
    return image_data;

# Get image_data and image_type from request
def get_image_data_from_request(req):
    # Three possible types, file, base64, url
    # They can send base64 and url by either form-data or json
    # They can send image (as a file) via form-data
    json_data = req.get_json(silent=True);
    form = req.form;
    files = req.files;

    # return None, None
    if (not files and not form and not json_data):
        return None, None;

    # Check for file upload
    if "image" in files:
        return files["image"], "file";

    # Check for form data
    if ("img_base64" in form):
        return form["img_base64"], "base64";
    if ("img_url" in form):
        return form["img_url"], "url";

    # Check for JSON data
    if (json_data):
        if ("img_base64" in json_data):
            return json_data["img_base64"], "base64";
        if ("img_url" in json_data):
            return json_data["img_url"], "url";

    return None, None;

# Check if the file extension and MIME type are allowed
def allowed_file(filename, mimetype):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS and \
        mimetype in ALLOWED_MIME_TYPES

# API route for removing the background from an image
@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    # Authenticate the user
    api_key = request.headers.get("x-api-key");
    authenticated = Authenticate(api_key);

    # If the user is not authenticated, return an error
    if (authenticated == False):
        return jsonify({"error": "Unauthorized"}), 401;

    # Get the image data and input type
    image_data, input_type = get_image_data_from_request(request);

    # Check if an image was provided either as a file or base64 string
    if (image_data is None or input_type is None):
        return jsonify({"error": "Could not find an image"}), 400;
    
    # Check the file extension and MIME type
    if (input_type == "file"):
        if (not allowed_file(image_data.filename, image_data.mimetype)):
            return jsonify({"error": "Image Format is not supported"}), 400;
        
    # Open the image with PIL
    input_image = get_image_data(image_data, input_type);
        
    # Check the file size
    file_size = len(input_image);

    # If the file size exceeds the maximum limit, return an error
    if (file_size > MAX_FILE_SIZE):
        return jsonify({"error": f"The file data exceeds the maximum size of {MAX_FILE_SIZE / (1024 * 1024)} MB"}), 400;
    
    # Remove the background from the image
    output_image = remove(input_image);

    # Create BytesIO object to handle the image data
    img_io = io.BytesIO();
    img_io.write(output_image);
    img_io.seek(0);

    app.logger.info("Image processed successfully!");

    # Return the image directly
    return send_file(img_io, mimetype="image/png");

# Route for the index page
@app.route("/")
def index():
    return jsonify({"message": "Background Remover API is up and ready!", "success": True});

app.logger.info("Starting the server...");
app.logger.info(f"Debug mode: {config['debug']}");

if (__name__ == "__main__"):
    app.run(debug=config["debug"]);