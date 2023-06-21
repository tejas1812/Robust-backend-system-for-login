# Use a base image with Python installed
FROM python:3.9

# Set the working directory in the container
WORKDIR /service

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port on which the application will run
EXPOSE 8000

# Set the environment variables
ENV FLASK_APP=service.py

# Run the application
CMD ["flask", "run", "--host", "0.0.0.0"]