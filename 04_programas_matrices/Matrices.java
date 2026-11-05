
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Locale;
import java.util.StringTokenizer;

public class Matrices {
    static final int CALENTAMIENTOS = 2;
    static final int REPETICIONES = 10;

    // Lee exactamente N x N valores antes de iniciar las mediciones.
    static double[] cargarMatriz(Path ruta, int n) throws IOException {
        double[] datos = new double[n * n];
        try (BufferedReader archivo = Files.newBufferedReader(ruta, StandardCharsets.US_ASCII)) {
            String primera = archivo.readLine();
            if (primera == null || Integer.parseInt(primera.trim()) != n) {
                throw new IOException("Tamaño incorrecto en " + ruta);
            }
            int posicion = 0;
            String linea;
            while ((linea = archivo.readLine()) != null) {
                StringTokenizer valores = new StringTokenizer(linea);
                while (valores.hasMoreTokens()) {
                    if (posicion >= datos.length) {
                        throw new IOException("Sobran datos en " + ruta);
                    }
                    datos[posicion++] = Double.parseDouble(valores.nextToken());
                }
            }
            if (posicion != datos.length) {
                throw new IOException("Matriz incompleta: " + ruta);
            }
        }
        return datos;
    }

    static void multiplicar(double[] a, double[] b, double[] c, int n) {
        for (int fila = 0; fila < n; fila++) {
            for (int columna = 0; columna < n; columna++) {
                double suma = 0.0;
                for (int paso = 0; paso < n; paso++) {
                    suma += a[fila * n + paso] * b[paso * n + columna];
                }
                c[fila * n + columna] = suma;
            }
        }
    }

    // Verifica la suma total y tres celdas fuera del intervalo medido.
    static void validar(double[] c, int n, double[] control) {
        double total = 0.0;
        for (double valor : c) {
            total += valor;
        }
        int centro = (n / 2) * n + n / 2;
        if (total != control[0] || c[0] != control[1]
                || c[centro] != control[2] || c[c.length - 1] != control[3]) {
            throw new IllegalStateException("La multiplicación no pasó la validación.");
        }
    }

    static void principal(String[] argumentos) throws IOException {
        // 1. Revisar el argumento y las mediciones existentes.
        if (argumentos.length != 1 || !(
                argumentos[0].equals("500")
                || argumentos[0].equals("1000")
                || argumentos[0].equals("1500"))) {
            throw new IllegalArgumentException(
                "Uso: java -cp 01_entornos/bin Matrices 500 (o 1000 o 1500)"
            );
        }
        int n = Integer.parseInt(argumentos[0]);
        Path carpeta = Path.of("03_crear matrices", Integer.toString(n));
        Path salida = Path.of("06_resultados", "java.csv");
        String cabecera = "language,N,repetition,time_seconds";
        boolean nuevo = !Files.exists(salida) || Files.size(salida) == 0;
        if (!nuevo) {
            try (BufferedReader anterior = Files.newBufferedReader(salida, StandardCharsets.UTF_8)) {
                if (!cabecera.equals(anterior.readLine())) {
                    throw new IOException("El CSV tiene un encabezado diferente.");
                }
                String linea;
                while ((linea = anterior.readLine()) != null) {
                    String[] campos = linea.split(",");
                    if (campos.length == 4 && campos[1].equals(Integer.toString(n))) {
                        throw new IOException(
                            "Este tamaño ya tiene filas. Conserva los CSV antes de repetir."
                        );
                    }
                }
            }
        }

        // 2. Cargar A, B y las referencias con el reloj detenido.
        double[] a = cargarMatriz(carpeta.resolve("a.txt"), n);
        double[] b = cargarMatriz(carpeta.resolve("b.txt"), n);
        String[] valores = Files.readString(
            carpeta.resolve("control.txt"), StandardCharsets.US_ASCII
        ).trim().split("\\s+");
        if (valores.length != 5 || Integer.parseInt(valores[0]) != n) {
            throw new IOException("El archivo de control no corresponde al tamaño.");
        }
        double[] control = new double[4];
        for (int posicion = 0; posicion < 4; posicion++) {
            control[posicion] = Double.parseDouble(valores[posicion + 1]);
        }

        // 3. Preparar la salida antes de cualquier medición.
        Files.createDirectories(salida.getParent());
        // Se reutiliza C: el algoritmo sobrescribe todas sus posiciones.
        double[] c = new double[n * n];
        try (BufferedWriter archivo = Files.newBufferedWriter(
                salida, StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            if (nuevo) {
                archivo.write(cabecera + "\n");
            }

            // 4. Excluir dos calentamientos y guardar diez mediciones.
            for (int ejecucion = 1; ejecucion <= CALENTAMIENTOS + REPETICIONES; ejecucion++) {
                // Solo la multiplicación queda entre las dos lecturas del reloj.
                long inicio = System.nanoTime();
                multiplicar(a, b, c, n);
                long fin = System.nanoTime();
                double segundos = (fin - inicio) / 1_000_000_000.0;
                validar(c, n, control);
                if (ejecucion > CALENTAMIENTOS) {
                    int repeticion = ejecucion - CALENTAMIENTOS;
                    archivo.write(String.format(
                        Locale.ROOT, "java,%d,%d,%.9f%n", n, repeticion, segundos
                    ));
                    archivo.flush();
                    System.out.printf(
                        Locale.ROOT, "java | N=%d | repetición=%d | %.9f s%n",
                        n, repeticion, segundos
                    );
                } else {
                    System.out.printf("java | N=%d | calentamiento %d/2%n", n, ejecucion);
                }
            }
        }
    }

    public static void main(String[] argumentos) {
        try {
            principal(argumentos);
        } catch (IOException | RuntimeException error) {
            System.err.println("Error: " + error.getMessage());
            System.exit(1);
        }
    }
}
