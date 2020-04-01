FROM python:3.5-slim

WORKDIR /geoip
COPY requirements.txt requirements.txt
RUN pip install -U pip && \
        pip install -r requirements.txt

COPY *.py geoname2fips.csv ./

ENTRYPOINT ["./geolite2legacy.py"]
