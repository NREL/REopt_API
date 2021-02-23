FROM julia:1.5.3

# # Install NREL root certs for machines running on NREL's network.
# ARG NREL_ROOT_CERT_URL_ROOT=""
# RUN set -x && if [ -n "$NREL_ROOT_CERT_URL_ROOT" ]; then curl -fsSLk -o /usr/local/share/ca-certificates/nrel_root.crt "${NREL_ROOT_CERT_URL_ROOT}/nrel_root.pem" && curl -fsSLk -o /usr/local/share/ca-certificates/nrel_xca1.crt "${NREL_ROOT_CERT_URL_ROOT}/nrel_xca1.pem" &&  update-ca-certificates; fi
# ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install Xpress solver for client
ENV XPRESSDIR=/opt/xpressmp
ENV XPRESS=/opt/xpressmp/bin
ENV LD_LIBRARY_PATH=${XPRESSDIR}/lib:${SRC_DIR}:${LD_LIBRARY_PATH}
ENV LIBPATH=${XPRESSDIR}/lib:${LIBPATH}
ENV PYTHONPATH=${XPRESSDIR}/lib:${PYTHONPATH}
ARG CLASSPATH=${XPRESSDIR}/lib/xprs.jar:${CLASSPATH}
ARG CLASSPATH=${XPRESSDIR}/lib/xprb.jar:${CLASSPATH}
ENV CLASSPATH=${XPRESSDIR}/lib/xprm.jar:${CLASSPATH}
ENV PATH=${XPRESSDIR}/bin:${PATH}

# WORKDIR /opt/reopt/solver
# COPY solver/install.sh .
# COPY solver/xp8.0.4_linux_x86_64.tar.gz .
# RUN sed -i -e 's/\r$//' install.sh
# ARG XPRESS_LICENSE_HOST=lcssvr
# RUN set -x && printf "f\nc\n\nn\nn\ny\n${XPRESS_LICENSE_HOST}\ny\n" | ./install.sh >> license_info.txt;
# RUN rm xp8.0.4_linux_x86_64.tar.gz

# Install Julia packages
WORKDIR /opt/julia_src/
COPY api.jl .
COPY Project.toml .
RUN julia --project="." -e 'import Pkg; Pkg.instantiate();' 
# TODO include("buildpkgs.jl")

# Build Julia system image
# WORKDIR /opt/reopt/julia_envs/Xpress/
# RUN julia --project="." -e 'import Pkg; Pkg.instantiate(); include("build_julia_image.jl"); build_julia_image("/opt/reopt/")'

CMD ["julia", "--project='.'", "&&", "include(\"api.jl\")"]