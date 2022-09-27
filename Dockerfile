# Google Cloud SDK docker image with GCP Python libs and helper tools

# Build container
FROM google/cloud-sdk:395.0.0 AS build
WORKDIR /home/cloudsdk/app
RUN chown cloudsdk:cloudsdk /home/cloudsdk/app
USER cloudsdk
ADD --chown=cloudsdk:cloudsdk . /home/cloudsdk/app
ENV PATH="${PATH}:/home/cloudsdk/.local/bin"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip3 install -q pybuilder==0.13.7 flake8==4.0.1 twine==4.0.1
RUN pyb -q install

#Upload the built python packge to pypi
ARG PYPI_USERNAME
ARG PYPI_PASSWORD
RUN set -e && if [ "$PYPI_USERNAME" != "" ]; then twine upload /home/cloudsdk/app/target/dist/stanford-wdl-kit-1.2.3/dist/* -u $PYPI_USERNAME -p $PYPI_PASSWORD ; fi;

# Final container, copies package from above
FROM google/cloud-sdk:395.0.0
WORKDIR /home/cloudsdk/app
RUN chown cloudsdk:cloudsdk /home/cloudsdk/app
RUN apt-get install -y zip
USER cloudsdk
COPY --chown=cloudsdk:cloudsdk --from=build /home/cloudsdk/app/target/dist/stanford-wdl-kit-1.2.3/dist/stanford-wdl-kit-1.2.3.tar.gz /home/cloudsdk/app
ADD --chown=cloudsdk:cloudsdk requirements.txt .
ENV PATH="${PATH}:/home/cloudsdk/.local/bin"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip3 install -q -r requirements.txt 
RUN pip3 install -q stanford-wdl-kit-*.tar.gz
WORKDIR /home/cloudsdk
RUN rm -rf app
