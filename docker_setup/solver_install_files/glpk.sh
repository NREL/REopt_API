#!/bin/bash
curl -O http://ftp.gnu.org/gnu/glpk/glpk-4.57.tar.gz \
	&& tar -zxvf glpk-4.57.tar.gz

## Verify package contents
# RUN wget http://ftp.gnu.org/gnu/glpk/glpk-4.57.tar.gz.sig \
#	&& gpg --verify glpk-4.57.tar.gz.sig
#	#&& gpg --keyserver keys.gnupg.net --recv-keys 5981E818

cd glpk-4.57
./configure && make && make check && make install && make distclean && ldconfig \
# Cleanup
rm -rf glpk-4.57.tar.gz && apt-get clean