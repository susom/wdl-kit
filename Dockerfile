# Google Cloud SDK docker image with GCP Python libs and helper tools

ARG CLOUD_SDK_VERSION=563.0.0

# Build container
FROM google/cloud-sdk:${CLOUD_SDK_VERSION} AS build
WORKDIR /home/cloudsdk/app
RUN chown cloudsdk:cloudsdk /home/cloudsdk/app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
USER cloudsdk
ADD --chown=cloudsdk:cloudsdk . /home/cloudsdk/app
ENV PATH="${PATH}:/home/cloudsdk/.local/bin"
ENV UV_COMPILE_BYTECODE=1
RUN uv build

# Upload the built python package to pypi
ARG PYPI_USERNAME
ARG PYPI_PASSWORD
RUN set -e && if [ "$PYPI_USERNAME" != "" ]; then uvx twine upload dist/* -u $PYPI_USERNAME -p $PYPI_PASSWORD ; fi

# Final container, copies package from above
ARG CLOUD_SDK_VERSION=563.0.0
FROM google/cloud-sdk:${CLOUD_SDK_VERSION}
WORKDIR /home/cloudsdk/app
RUN chown cloudsdk:cloudsdk /home/cloudsdk/app
RUN apt-get install -y zip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
COPY --chown=cloudsdk:cloudsdk --from=build /home/cloudsdk/app/dist/stanford_wdl_kit-1.9.7-*.whl /home/cloudsdk/app/
RUN uv pip install --system --break-system-packages stanford_wdl_kit-*.whl
USER cloudsdk
ENV PATH="${PATH}:/home/cloudsdk/.local/bin"
WORKDIR /home/cloudsdk
RUN rm -rf app
