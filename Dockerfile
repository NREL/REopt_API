FROM python:3-onbuild

ENV PYTHONDONTWRITEBYTECODE 1
ADD . /opt/reopt
WORKDIR /opt/reopt
ENV APP_ENV=local

EXPOSE 8000
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
