# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir flask gunicorn werkzeug

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches, using gunicorn as the WSGI server
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]

