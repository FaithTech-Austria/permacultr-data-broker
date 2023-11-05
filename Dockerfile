# Use an official Python runtime as a parent image
#FROM python:3.9-slim-buster
FROM continuumio/miniconda3
#FROM thinkwhere/gdal-python

# Set the working directory to /code
WORKDIR /code

COPY requirements.txt .
RUN conda install -c conda-forge gdal
RUN pip install -r requirements.txt


COPY /app /code/app
RUN mkdir /code/data
COPY .env .


# Run main.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]



