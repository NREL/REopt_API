#Download base image ubuntu 16.04
FROM ubuntu:16.04



MAINTAINER REopt Team, NREL Energy Modeling & Analysis <REopt@nrel.gov>



## Get Required Software
RUN apt-get update \
	&& apt-get upgrade -y \
	&& apt update -y \
	&& apt install libsqlite3-dev build-essential python3-pip virtualenv libssl-dev libbz2-dev lzma -y\
	&&  apt-get install -y build-essential git curl zlib1g-dev\
	   python-software-properties software-properties-common \
	   python-dev \
	   python-setuptools --no-install-recommends -y \
	&& pip3 install --upgrade pip && apt-get install postgresql \
		postgresql-contrib postgresql-client-common postgresql-client redis-server -y \
	&& rm -rf /var/lib/apt 
RUN mkdir -p /data/github && cd /data/github



## Python
WORKDIR /usr/src
RUN curl -O  https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
RUN tar xzf Python-3.6.8.tgz && rm Python-3.6.8.tgz
WORKDIR Python-3.6.8
RUN ./configure --enable-optimizations --enable-loadable-sqlite-extensions  --enable-shared
RUN make altinstall



## Set Up Database
USER postgres
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER reopt WITH PASSWORD 'reopt'; ALTER USER reopt CREATEDB;" &&\
    createdb reopt reopt &&\
    psql --command "GRANT ALL PRIVILEGES ON DATABASE reopt TO reopt;"    
USER root



## Set Up Solver
ARG solver=solver
ENV SOLVER=$solver

ENV XPRESSDIR=/opt/xpressmp
ENV XPRESS=/opt/xpressmp/bin
ENV LD_LIBRARY_PATH=${XPRESSDIR}/lib:${LD_LIBRARY_PATH}
ENV DYLD_LIBRARY_PATH=${XPRESSDIR}/lib:${DYLD_LIBRARY_PATH}
ENV LIBPATH=${XPRESSDIR}/lib:${LIBPATH}
ENV PYTHONPATH=${XPRESSDIR}/lib:${PYTHONPATH}

ARG CLASSPATH=${XPRESSDIR}/lib/xprs.jar:${CLASSPATH}
ARG CLASSPATH=${XPRESSDIR}/lib/xprb.jar:${CLASSPATH}
ENV CLASSPATH=${XPRESSDIR}/lib/xprm.jar:${CLASSPATH}
ENV PATH=${XPRESSDIR}/bin:${PATH}


RUN mkdir /to_share
RUN mkdir /solver_install_files
COPY solver_install_files /solver_install_files/
WORKDIR /
RUN if [ "$solver" = "xpress" ] ; then printf 'y\ns\n"/opt/xpressmp"\nn\nn\ny\n' | ./solver_install_files/xpress_files/install.sh >> /to_share/license_info.txt; fi
RUN if [ "$solver" = "glpk" ] ; then chmod +x . /solver_install_files/glpk.sh; fi
RUN if [ "$solver" = "glpk" ] ; then ./solver_install_files/glpk.sh; fi

												   

## Get Latest REopt Code
ARG github_username
ARG github_password
WORKDIR /data/github/
RUN git clone --single-branch --branch develop https://$github_username:$github_password@github.com/NREL/reopt_api.git
WORKDIR /data/github/reopt_api
ENV LD_LIBRARY_PATH=/usr/src/Python-3.6.8/:${LD_LIBRARY_PATH}
RUN virtualenv env --python=/usr/local/bin/python3.6
ENV PATH=/data/github/reopt_api/env/bin:$PATH
ENV APP_ENV=local
RUN pip install -r requirements.txt --exists-action w


## Get Julia and dependencies
WORKDIR /usr/src
RUN curl -Ok https://julialang-s3.julialang.org/bin/linux/x64/1.2/julia-1.2.0-linux-x86_64.tar.gz
RUN tar xvfz julia-1.2.0-linux-x86_64.tar.gz && rm julia-1.2.0-linux-x86_64.tar.gz
ENV PATH=/usr/src/julia-1.2.0/bin:$PATH
ENV LD_PRELOAD=/usr/src/julia-1.2.0/lib/julia/libstdc++.so.6

WORKDIR /data/github/reopt_api
RUN python -c 'import julia; julia.install()'
RUN julia -e 'import Pkg; \
              Pkg.update(); \
              ENV["PYTHON"] = "/data/github/reopt_api/env/bin/python"; \
              Pkg.add(Pkg.PackageSpec(url="https://github.com/JuliaOpt/Xpress.jl.git")); \
              Pkg.add(Pkg.PackageSpec(name="JuMP", version="0.19.2")); \
              Pkg.add(Pkg.PackageSpec(name="AxisArrays", version="0.3.3")); \
              Pkg.add(Pkg.PackageSpec(name="MathOptInterface", version="0.8.4"))'

EXPOSE 8000

COPY startupscript.sh /data/startupscript.sh
RUN sed -i.bak  's/<SOLVER>/$solver/g' /data/startupscript.sh 
RUN chmod +x . /data/startupscript.sh
ENTRYPOINT ["/data/startupscript.sh"]
