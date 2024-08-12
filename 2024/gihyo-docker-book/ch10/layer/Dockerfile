FROM ubuntu:23.10

ARG GH_VERSION=2.33.0

RUN apt update

RUN apt install -y curl

RUN curl -L -O https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz

RUN tar xvzf gh_${GH_VERSION}_linux_amd64.tar.gz

RUN mv gh_${GH_VERSION}_linux_amd64/bin/gh /usr/local/bin

RUN rm -rf gh_${GH_VERSION}_linux_amd64*
RUN apt purge -y curl
RUN apt clean
RUN rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "gh" ]