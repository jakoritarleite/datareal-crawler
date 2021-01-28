FROM amazonlinux:latest

# Requirements to compile openssl
RUN yum install -y make glibc-devel gcc patch tar gzip perl-core zlib-devel git
RUN curl https://www.openssl.org/source/openssl-1.1.1i.tar.gz --output .
# COPY openssl-1.1.1i.tar.gz .
RUN tar xf openssl-1.1.1i.tar.gz

# Compile OpenSSL
WORKDIR openssl-1.1.1i/
RUN ./config --prefix=/usr/local/ssl --openssldir=/usr/local/ssl shared zlib
RUN make
RUN make test
RUN make install

# Install Rustc and Cargo
RUN curl https://sh.rustup.rs -sSf | sh

# Download Crawler Source
RUN git clone https://github.com/jakoritarleite/datareal-crawler.git

# Copy OpenSSL libraries
RUN cp libopenssl.so* datareal-crawler/lib/
RUN cp libcrypto.so* datareal-crawler/lib/

# Compile Rust code
WORKDIR datareal-crawler/
RUN ./scripts/build_rust.sh