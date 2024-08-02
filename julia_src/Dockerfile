FROM julia:1.10.2

# Install NREL root certs for machines running on NREL's network.
ARG NREL_ROOT_CERT_URL_ROOT=""
RUN set -x && if [ -n "$NREL_ROOT_CERT_URL_ROOT" ]; then curl -fsSLk -o /usr/local/share/ca-certificates/nrel_root.crt "${NREL_ROOT_CERT_URL_ROOT}/nrel_root.pem" && curl -fsSLk -o /usr/local/share/ca-certificates/nrel_xca1.crt "${NREL_ROOT_CERT_URL_ROOT}/nrel_xca1.pem" &&  update-ca-certificates; fi
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install Julia packages
ENV JULIA_NUM_THREADS=2
ENV XPRESS_JL_SKIP_LIB_CHECK=True

WORKDIR /opt/julia_src
COPY . .
RUN julia --project=/opt/julia_src -e 'import Pkg; Pkg.instantiate();'
RUN julia --project=/opt/julia_src precompile.jl
EXPOSE 8081

CMD ["bash"]
