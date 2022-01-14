FROM python:3.8
# Used to create base python image for REopt app with requirements installed to speed up other builds

ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /opt/reopt
COPY requirements.txt .

# Install python packages
RUN ["pip", "install", "-r", "requirements.txt"]

ENTRYPOINT ["/bin/bash", "-c"]