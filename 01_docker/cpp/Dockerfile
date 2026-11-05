FROM gcc@sha256:43978d7710a803d1c3d32f4117c1528ec7285a4ce2c0a51e982ec1a6e3d87d95

WORKDIR /app

COPY ["04_programas_matrices/matrices.cpp", "04_programas_matrices/matrices.cpp"]

RUN mkdir -p bin 06_resultados \
    && g++ -O2 -std=c++17 -fno-fast-math -ffp-contract=off \
       04_programas_matrices/matrices.cpp -o bin/matrices

COPY ["03_crear matrices/", "03_crear matrices/"]

ENTRYPOINT ["/app/bin/matrices"]