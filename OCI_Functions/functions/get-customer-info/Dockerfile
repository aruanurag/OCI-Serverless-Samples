FROM fnproject/go:1.24-dev as build-stage
WORKDIR /function
WORKDIR /go/src/func/
ENV GO111MODULE=on
COPY . .
RUN go mod tidy
RUN go build -o func -v
FROM fnproject/go:1.24
WORKDIR /function
COPY --from=build-stage /go/src/func/func /function/
ENTRYPOINT ["./func"]