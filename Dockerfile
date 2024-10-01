# Use the official Python image from the Docker Hub
FROM python:3.12

RUN pip install setuptools

RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
