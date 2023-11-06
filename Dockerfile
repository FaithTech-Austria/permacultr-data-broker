# Use an official Python runtime as a parent image
#FROM python:3.9-slim-buster
FROM continuumio/miniconda3
#FROM thinkwhere/gdal-python

# Set the working directory to /code
WORKDIR /code

ADD environment/environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

COPY environment/requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir data/
COPY /app /code/app
COPY .env .

# Run main.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]



