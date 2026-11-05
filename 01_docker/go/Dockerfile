FROM golang@sha256:972b4110ba0f47539a975c31e52c64765e1ff19f2d74469ae4a595c6676e80a5

WORKDIR /app

ENV GOMAXPROCS=1

COPY ["04_programas_matrices/matrices.go", "04_programas_matrices/matrices.go"]

RUN mkdir -p bin 06_resultados \
    && go build -o bin/matrices 04_programas_matrices/matrices.go

COPY ["03_crear matrices/", "03_crear matrices/"]

ENTRYPOINT ["/app/bin/matrices"]