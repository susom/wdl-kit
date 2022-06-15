# Google Cloud SDK docker image with GCP Python libs and helper tools
FROM google/cloud-sdk:367.0.0 AS build

WORKDIR /code
ADD . /code
RUN pip3 install pybuilder==0.13.5
RUN pyb install 

FROM google/cloud-sdk:367.0.0
WORKDIR /opt/wdl-kit
COPY --from=build /code/target/dist/wdl-kit-1.0.0/dist/wdl-kit-1.0.0.tar.gz /opt/wdl-kit/
ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install wdl-kit-*.tar.gz
RUN apt-get install -y zip
