FROM continuumio/miniconda3
#FROM thinkwhere/gdal-python

# Set the working directory to /code
WORKDIR /code

ADD requirements/environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

COPY requirements/requirements.txt .
RUN pip install -r requirements.txt

COPY app /code/appy

# Run main.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]