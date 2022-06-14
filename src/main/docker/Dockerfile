# Google Cloud SDK docker image with GCP Python libs and helper tools
FROM google/cloud-sdk:${GCLOUD_SDK_VERSION:-367.0.0} as google-cloud-sdk
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get install -y zip

