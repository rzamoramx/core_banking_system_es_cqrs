FROM golang:1.23-alpine3.20 AS builder
WORKDIR /app

# Copy the go code
COPY es /app/es
WORKDIR /app/es

# Download dependencies and build
RUN go mod download
RUN go build -o main .

FROM alpine:3.20
WORKDIR /app
# Copy the built binary
COPY --from=builder /app/es/main .
# Copy configuration file if exists
COPY --from=builder /app/es/config-dev.json . 

EXPOSE 8002
ENTRYPOINT ["./main"]
