# Use an official Python runtime as a parent image
#FROM python:3.9-slim-buster
#FROM continuumio/miniconda3

FROM thinkwhere/gdal-python

# Set the working directory to /code
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /app .
COPY .env .
COPY requirements.txt .
RUN mkdir data 


#RUN conda install python=3.9

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Install GDAL and other system dependencies with Conda
#RUN conda install -c conda-forge gdal


# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]



