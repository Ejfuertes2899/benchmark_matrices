
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int CALENTAMIENTOS = 2;
constexpr int REPETICIONES = 10;

// Lee exactamente N x N valores de doble precisión.
std::vector<double> cargar_matriz(const std::string& ruta, int n) {
    std::ifstream archivo(ruta);
    int tamano = 0;
    if (!(archivo >> tamano) || tamano != n) {
        throw std::runtime_error("No pude leer la matriz: " + ruta);
    }
    std::vector<double> datos(n * n);
    for (double& valor : datos) {
        if (!(archivo >> valor)) {
            throw std::runtime_error("Matriz incompleta: " + ruta);
        }
    }
    std::string extra;
    if (archivo >> extra) {
        throw std::runtime_error("Sobran datos en: " + ruta);
    }
    return datos;
}

void multiplicar(
    const std::vector<double>& a, const std::vector<double>& b,
    std::vector<double>& c, int n
) {
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

// Comprueba la suma total y tres celdas después de detener el reloj.
void validar(const std::vector<double>& c, int n, const std::vector<double>& control) {
    double total = 0.0;
    for (double valor : c) {
        total += valor;
    }
    int centro = (n / 2) * n + n / 2;
    if (total != control[0] || c[0] != control[1]
        || c[centro] != control[2] || c.back() != control[3]) {
        throw std::runtime_error("La multiplicación no pasó la validación.");
    }
}

int main(int cantidad, char* argumentos[]) {
    try {
        std::locale::global(std::locale::classic());
        static_assert(
            sizeof(double) == 8 && std::numeric_limits<double>::is_iec559,
            "Se requiere double IEEE de 64 bits."
        );

        // 1. Revisar el argumento y los resultados anteriores.
        if (cantidad != 2 || (
            std::string(argumentos[1]) != "500"
            && std::string(argumentos[1]) != "1000"
            && std::string(argumentos[1]) != "1500"
        )) {
            throw std::runtime_error("Uso: 01_entornos/bin/cpp.exe 500 (o 1000 o 1500)");
        }
        int n = std::stoi(argumentos[1]);
        std::string carpeta = "03_crear matrices/" + std::to_string(n) + "/";
        std::string ruta_salida = "06_resultados/cpp.csv";
        std::string cabecera = "language,N,repetition,time_seconds";
        std::ifstream anterior(ruta_salida);
        std::string linea;
        bool nuevo = !std::getline(anterior, linea);
        if (!nuevo && linea != cabecera && linea != cabecera + "\r") {
            throw std::runtime_error("El CSV tiene un encabezado diferente.");
        }
        while (std::getline(anterior, linea)) {
            if (linea.find("," + std::to_string(n) + ",") != std::string::npos) {
                throw std::runtime_error("Este tamaño ya tiene filas. Conserva los CSV antes de repetir.");
            }
        }
        anterior.close();

        // 2. Cargar las entradas y las referencias sin medir su lectura.
        std::vector<double> a = cargar_matriz(carpeta + "a.txt", n);
        std::vector<double> b = cargar_matriz(carpeta + "b.txt", n);
        std::ifstream referencia(carpeta + "control.txt");
        int tamano = 0;
        std::vector<double> control(4);
        if (!(referencia >> tamano) || tamano != n) {
            throw std::runtime_error("El archivo de control no corresponde al tamaño.");
        }
        for (double& valor : control) {
            if (!(referencia >> valor)) {
                throw std::runtime_error("El archivo de control está incompleto.");
            }
        }

        // 3. Preparar el archivo y la matriz de salida.
        std::filesystem::create_directories("06_resultados");
        std::ofstream salida(ruta_salida, std::ios::app);
        salida.exceptions(std::ios::badbit | std::ios::failbit);
        salida << std::fixed << std::setprecision(9);
        if (nuevo) {
            salida << cabecera << '\n';
        }
        // C se reserva una vez. Cada multiplicación sobrescribe todas sus celdas.
        std::vector<double> c(n * n, 0.0);

        // 4. Excluir los calentamientos y registrar diez mediciones.
        for (int ejecucion = 1; ejecucion <= CALENTAMIENTOS + REPETICIONES; ejecucion++) {
            // Solo esta llamada queda dentro del intervalo medido.
            auto inicio = std::chrono::steady_clock::now();
            multiplicar(a, b, c, n);
            auto fin = std::chrono::steady_clock::now();
            double segundos = std::chrono::duration<double>(fin - inicio).count();
            validar(c, n, control);
            if (ejecucion > CALENTAMIENTOS) {
                int repeticion = ejecucion - CALENTAMIENTOS;
                salida << "cpp," << n << ',' << repeticion << ',' << segundos << '\n';
                salida.flush();
                std::cout << "cpp | N=" << n << " | repetición=" << repeticion
                          << " | " << segundos << " s" << std::endl;
            } else {
                std::cout << "cpp | N=" << n << " | calentamiento " << ejecucion << "/2" << std::endl;
            }
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << std::endl;
        return 1;
    }
}
