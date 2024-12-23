# Use the official Python 3.10 slim base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install curl because it's not present in the slim image
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the necessary dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port on which the Flask application runs
EXPOSE 5000

# Download the pre-trained U-2-Net model
RUN mkdir u2net && curl -L https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx -o u2net/u2net.onnx

# Command to launch the application using Gunicorn
CMD ["gunicorn", "--workers", "3", "--timeout", "800", "--bind", "0.0.0.0:5000", "app:app"]
