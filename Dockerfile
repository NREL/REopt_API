FROM python:3-onbuild

ENV PYTHONDONTWRITEBYTECODE 1
ADD . /opt/reopt
ENV APP_ENV=local
ENV SRC_DIR=/opt/reopt/src

RUN apt update -y && apt install -y coinor-cbc;  # TODO: docker push container with cbc

# Install Julia and Packages  TODO: use Julia image and CMD the rest?
WORKDIR /usr/src
RUN curl -Ok https://julialang-s3.julialang.org/bin/linux/x64/1.2/julia-1.2.0-linux-x86_64.tar.gz
RUN tar xvfz julia-1.2.0-linux-x86_64.tar.gz && rm julia-1.2.0-linux-x86_64.tar.gz
ENV PATH=/usr/src/julia-1.2.0/bin:$PATH
ENV LD_PRELOAD=/usr/src/julia-1.2.0/lib/julia/libstdc++.so.6
RUN python -c 'import julia; julia.install()'
RUN julia -e 'import Pkg; \
              Pkg.update(); \
              ENV["PYTHON"] = "/data/github/reopt_api/env/bin/python"; \
              Pkg.add("Cbc"); \
              Pkg.add("JuMP"); \
              Pkg.add("AxisArrays"); \
              Pkg.add("MathOptInterface")'

WORKDIR /opt/reopt
EXPOSE 8000
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
