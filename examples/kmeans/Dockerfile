FROM registry.spartzinc.com:5000/dose_scipy27:latest
MAINTAINER Troy de Freitas troy@dose.com

RUN pip install sklearn

RUN pip install docopt

COPY . /opt

RUN mkdir /opt/model

ENTRYPOINT ["python", "/opt/model.py"]
