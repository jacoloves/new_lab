FROM --platform=$BUILDPLATFORM ubuntu:23.10 AS build

ARG TARGETARCH

RUN apt update
RUN apt install -y curl

RUN curl -L -o /tmp/jq https://github.com/jqlang/jq/releases/download/jq-1.7/jq-linux-${TARGETARCH}
RUN chmod +x /tmp/jq

FROM gcr.io/distroless/base-debian11:debug

COPY --from=build /tmp/jq /usr/local/bin
COPY show-attr.sh /usr/local/bin

ENTRYPOINT [ "sh", "/usr/local/bin/show-attr.sh" ]
CMD [""]