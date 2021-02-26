FROM python:3.6

ENV SRC_DIR=/opt/reopt/reo/src
ENV LD_LIBRARY_PATH="/opt/reopt/reo/src:${LD_LIBRARY_PATH}"

# Copy all code
ENV PYTHONDONTWRITEBYTECODE 1
COPY . /opt/reopt

WORKDIR /opt/reopt/bin
RUN chmod +x wait-for-it.bash

# Install python packages
WORKDIR /opt/reopt
RUN ["pip", "install", "-r", "requirements.txt"]

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "-c"]
