FROM alpine:latest

MAINTAINER Christan Grant <cgrant@ou.edu>

# Usage docker build -t cegme/oulatin-search .
# docker run -dt -p 5000:5000 cegme/oulatin-search

RUN apk update
RUN apk add git curl vim strace tmux htop tar make
RUN apk add python3-dev tcl-dev gcc g++ libffi-dev
RUN apk add bash

RUN pip3 install --upgrade pip &&\
		pip3 install apsw nltk cltk flask beautifulsoup4 ipython html5lib flask-wtf flask-bootstrap

RUN pip3 install sqlitefts

RUN mkdir /src
RUN mkdir /src/templates

COPY ./search/buildcode.sh /src
COPY ./search/app.py /src
COPY ./search/search.py /src
COPY ./search/query.py /src
COPY ./search/search.html /src/templates
COPY ./search/search_results.html /src/templates
COPY ./search/interface.py /src

RUN cd /src && bash buildcode.sh

ADD . /phyllo
ADD . /search
RUN cd /phyllo && pip3 install .

# Download the database file to /src
RUN cd /src && python3 -c "import phyllo.data_extractor as d; d.main()"

#RUN cd /src && python3 -c "import app as f; f.tokenize()"

EXPOSE 5000
WORKDIR /src
#ENTRYPOINT ["python3"]
#CMD ["/src/app.py"]
