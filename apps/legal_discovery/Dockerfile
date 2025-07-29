# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update \
    && apt-get install -y nodejs npm \
    && npm --prefix apps/legal_discovery install \
    && npm --prefix apps/legal_discovery run build --silent \
    && rm -rf apps/legal_discovery/node_modules /var/lib/apt/lists/*

# Copy the rest of the application's code into the container
COPY . .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
ENV NAME World

# Run the Flask application via gunicorn with eventlet for SocketIO support
# Using "python -m" avoids PATH issues on Windows hosts
CMD ["python", "-m", "gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5001", "apps.legal_discovery.interface_flask:app"]
