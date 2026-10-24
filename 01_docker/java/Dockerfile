FROM eclipse-temurin@sha256:107215954359f1ab0be058a247d7c64ed6e69c71c1682d471d38ef751ec8e964

WORKDIR /app

COPY ["04_programas_matrices/Matrices.java", "04_programas_matrices/Matrices.java"]

RUN mkdir -p bin 06_resultados \
    && javac -encoding UTF-8 -d bin 04_programas_matrices/Matrices.java

COPY ["03_crear matrices/", "03_crear matrices/"]

ENTRYPOINT ["java", "-XX:ActiveProcessorCount=1", "-XX:+UseSerialGC", "-cp", "/app/bin", "Matrices"]