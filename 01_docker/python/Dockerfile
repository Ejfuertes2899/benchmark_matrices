FROM python@sha256:f06d01d4ba3f8ad5af45a3ec87df19c1d317d8e8961edc0fabda61811af6f7cf

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1

COPY ["04_programas_matrices/matrices.py", "04_programas_matrices/matrices.py"]

COPY ["03_crear matrices/", "03_crear matrices/"]

# Se conserva la ruta interna para los comandos e imagenes existentes.
COPY ["06_revisión de archivos/", "07_revisión de archivos/"]

RUN mkdir -p 06_resultados

ENTRYPOINT ["python", "-u", "04_programas_matrices/matrices.py"]