FROM python:3-onbuild

ENV PYTHONDONTWRITEBYTECODE 1
ADD . /opt/reopt
ENV APP_ENV=local

## Get Julia and dependencies
WORKDIR /usr/src
RUN curl -Ok https://julialang-s3.julialang.org/bin/linux/x64/1.2/julia-1.2.0-linux-x86_64.tar.gz
RUN tar xvfz julia-1.2.0-linux-x86_64.tar.gz && rm julia-1.2.0-linux-x86_64.tar.gz
ENV PATH=/usr/src/julia-1.2.0/bin:$PATH
ENV LD_PRELOAD=/usr/src/julia-1.2.0/lib/julia/libstdc++.so.6
RUN python -c 'import julia; julia.install()'
RUN julia -e 'import Pkg; \
              Pkg.update(); \
              ENV["PYTHON"] = "/data/github/reopt_api/env/bin/python"; \
              Pkg.add(Pkg.PackageSpec(url="https://github.com/JuliaOpt/Xpress.jl.git")); \
              Pkg.add(Pkg.PackageSpec(name="JuMP", version="0.19.2")); \
              Pkg.add(Pkg.PackageSpec(name="AxisArrays", version="0.3.3")); \
              Pkg.add(Pkg.PackageSpec(name="MathOptInterface", version="0.8.4"))'

WORKDIR /opt/reopt

EXPOSE 8000
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
