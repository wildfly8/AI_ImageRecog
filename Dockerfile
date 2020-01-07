# Starts with python:3.7.1-alpine and then installs most of python:2.7.15-alpine on top
# to allows us to choose Python versions at runtime via: python2, python3, pip2, pip3, etc.
FROM centos:7

ENV PYTHON_VERSION 3.7.1
ENV PYTHON_COMMAND python3
ENV SECRETS_LOCATION "/var/run"
ENV LOG_LOCATION "/var/log/gup"
# Updating Container
RUN yum -y update

# Installing tools to compile Python
RUN yum groupinstall -y "development tools"
RUN yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel
RUN yum install -y db4-devel libpcap-devel xz-devel expat-devel libffi-devel gcc
RUN yum install -y wget which

# Installing Python  version
# Based on https://danieleriksson.net/2017/02/08/how-to-install-latest-python-on-centos/

RUN cd /usr/src && \
    wget -O python.tar.tgz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-${PYTHON_VERSION}.tgz" && \
	tar xzf python.tar.tgz && \
	cd Python-${PYTHON_VERSION} && \
	./configure --enable-optimizations && \
	make install

# Update Pip for both environments
RUN cd /usr/src && \
	wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py --no-check-certificate && \
    ${PYTHON_COMMAND} get-pip.py --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org

### Installing Pre-requirements
RUN yum install -y mysql-devel mysql-lib libcurl-devel

# Install open jdk 8 (used for tika)
RUN yum install -y java-1.8.0-openjdk

ADD . /code
WORKDIR /code

RUN pip install -r requirements.txt

RUN chmod +x run.sh

RUN chmod +x src/updates.py

ENV PATH=$PATH:/code/wardini-scraper:/code

## Command line parameters default, could be overridden by docker run commands
##  It should be overrridden in the Autosys Job commands
CMD ["/bin/bash", "run.sh"]
