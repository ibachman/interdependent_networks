FROM python:3.8-slim

ADD Archive.zip /experiments/Archive.zip

RUN apt-get update -y && apt-get install -y unzip

WORKDIR /experiments/

RUN unzip Archive.zip

RUN pip3 install -r /experiments/requirements.txt
RUN pip3 install awscli

ADD run.sh /experiments/run.sh

ENTRYPOINT ["/experiments/run.sh"]