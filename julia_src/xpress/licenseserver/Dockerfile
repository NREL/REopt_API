FROM reopt/xpressbase AS xpress

FROM ubuntu:latest

# Install Xpress solver
ENV XPRESSDIR=/opt/xpressmp
ENV XPRESS=/opt/xpressmp/bin
ENV LD_LIBRARY_PATH=${XPRESSDIR}/lib:${SRC_DIR}:${LD_LIBRARY_PATH}
ENV LIBPATH=${XPRESSDIR}/lib:${LIBPATH}
ENV PYTHONPATH=${XPRESSDIR}/lib:${PYTHONPATH}
ARG CLASSPATH=${XPRESSDIR}/lib/xprs.jar:${CLASSPATH}
ARG CLASSPATH=${XPRESSDIR}/lib/xprb.jar:${CLASSPATH}
ENV CLASSPATH=${XPRESSDIR}/lib/xprm.jar:${CLASSPATH}
ENV PATH=${XPRESSDIR}/bin:${PATH}

WORKDIR ${XPRESS}
COPY --from=xpress  /opt/reopt/solver/ .
COPY xpauth.xpr .
RUN sed -i -e 's/\r$//' install.sh
RUN printf 'f\ns\n\ny\n.\ny\n' | ./install.sh >> license_info.txt;
RUN rm xp8.12.3_linux_x86_64.tar.gz

CMD xpserver