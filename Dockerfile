# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install gcc and other necessary build tools
RUN apt-get update && \
    apt-get install -y gcc build-essential

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app

# Expose port 5000 (the default port for Flask)
EXPOSE 8000

# Set the environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Use gunicorn as the WSGI server to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]