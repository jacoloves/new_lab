FROM golang:1.20.5

WORKDIR /go/src/github.com/gihyodocker/echo
COPY main.go .
RUN go mod init

CMD ["go", "run", "main.go"]
