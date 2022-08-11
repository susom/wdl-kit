# Google Cloud SDK docker image with GCP Python libs and helper tools
FROM google/cloud-sdk:395.0.0 AS build

WORKDIR /code
ADD . /code
RUN pip3 install pybuilder==0.13.7
RUN pyb install 

FROM google/cloud-sdk:395.0.0
WORKDIR /opt/wdl-kit
COPY --from=build /code/target/dist/stanford-wdl-kit-1.2.1/dist/stanford-wdl-kit-1.2.1.tar.gz /opt/wdl-kit/
ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install stanford-wdl-kit-*.tar.gz
RUN apt-get install -y zip
