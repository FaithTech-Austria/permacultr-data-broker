# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /code
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /app .
COPY .env .
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 80 for the API
EXPOSE 80

# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]



