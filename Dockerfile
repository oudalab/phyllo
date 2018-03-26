FROM alpine:latest

MAINTAINER Christan Grant <cgrant@ou.edu>

# Usage docker build -t cegme/phyllo .
# docker run -dt -p 5000:5000 cegme/phyllo

RUN apk update
RUN apk add git curl vim strace tmux htop tar make
RUN apk add python3-dev tcl-dev gcc g++ libffi-dev
RUN apk add bash

RUN pip3 install --upgrade pip &&\
		pip3 install nltk cltk flask beautifulsoup4 ipython html5lib flask-wtf flask-bootstrap

RUN apk update && apk add build-base git libffi-dev python3-dev wget
RUN apk add icu-dev icu-doc icu-libs file boost-dev --update alpine-sdk
RUN cd && wget http://www.sqlite.org/2017/sqlite-autoconf-3190300.tar.gz https://github.com/rogerbinns/apsw/releases/download/3.19.3-r1/apsw-3.19.3-r1.zip
RUN cd && tar zxvf sqlite-autoconf-3190300.tar.gz && cd sqlite-autoconf-3190300/ && CPPFLAGS="-DSQLITE_ENABLE_FTS4_TOKENIZER=1" ./configure && make install
# Trying this
RUN cd && unzip apsw-3.19.3-r1.zip && cd apsw-3.19.3-r1 && python3 setup.py build --enable-all-extensions install

RUN pip3 install git+git://github.com/hideaki-t/sqlite-fts-python.git@apsw
# RUN pip3 install git+git://github.com/oudalab/sqlite-fts-python.git

RUN pip3 install sqlitefts

RUN mkdir -p /src/templates

COPY ./search/buildcode.sh /src
COPY ./search/app.py /src
COPY ./search/search.py /src
COPY ./search/templates/* /src/templates/
COPY ./phyllo/phyllo_logger.py /src
COPY ./search/texts.db /src

#RUN cd /src && bash buildcode.sh

ADD . /phyllo
ADD . /search
# TODO debug this
# RUN cd /phyllo/phyllo/ && pip3 install .
RUN cd /phyllo/ && python3 setup.py install

# Download the database file to /src
#RUN cd /src && python3 -c "import phyllo.data_extractor as d; d.main()"

RUN ["chmod", "+x", "/src/app.py"]

#RUN cd /src && python3 -c "import app as f; f.tokenize()"

EXPOSE 5000
WORKDIR /src
#ENTRYPOINT ["python3"]
CMD ["python3","/src/app.py"]
