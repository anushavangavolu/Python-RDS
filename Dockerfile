# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including moreutils
RUN apt-get update && apt-get install -y \
    moreutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file for efficient caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the application's port (default Flask port is 5000)
# Expose the application port
EXPOSE 5000

# Set environment variables
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV DB_USERNAME=admin
ENV DB_ENDPOINT=database-1.cgtoqkc9cnse.us-east-1.rds.amazonaws.com
ENV DB_NAME=rds_usersdb
ENV JWT_SECRET_KEY=myjwtpythonsecret
ENV DB_PASSWORD_FILE=/run/secrets/db_password
ENV FLASK_APP=app.py

# Command to run the application
CMD ["flask", "run"]