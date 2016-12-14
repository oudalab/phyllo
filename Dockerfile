FROM alpine:latest

MAINTAINER Christan Grant <cgrant@ou.edu>

# Usage docker build -t cegme/oulatin-search .
# docker run -dt -p 5000:5000 cegme/oulatin-search

RUN apk update
RUN apk add git curl vim strace tmux htop tar make
RUN apk add python3-dev tcl-dev gcc g++ libffi-dev

RUN pip3 install --upgrade pip &&\
		pip3 install apsw nltk cltk flask

RUN pip3 install sqlitefts

RUN mkdir /src

COPY ./search/buildcode.sh /src
COPY ./search/app.py /src
COPY ./search/search.py /src

RUN cd /src && sh buildcode.sh

ADD ./phyllo /usr/local/bin

EXPOSE 5000
WORKDIR /src
ENTRYPOINT ["python3"]
CMD ["/src/app.py"]
