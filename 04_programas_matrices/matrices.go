
package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"time"
)

const calentamientos = 2
const repeticiones = 10

// cargarMatriz lee exactamente N x N números float64.
func cargarMatriz(ruta string, n int) ([]float64, error) {
	archivo, errorLectura := os.Open(ruta)
	if errorLectura != nil {
		return nil, errorLectura
	}
	defer archivo.Close()
	lector := bufio.NewReader(archivo)
	var tamano int
	if _, errorLectura = fmt.Fscan(lector, &tamano); errorLectura != nil || tamano != n {
		return nil, fmt.Errorf("tamaño incorrecto en %s", ruta)
	}
	datos := make([]float64, n*n)
	for posicion := range datos {
		if _, errorLectura = fmt.Fscan(lector, &datos[posicion]); errorLectura != nil {
			return nil, fmt.Errorf("matriz incompleta: %s", ruta)
		}
	}
	var extra string
	if _, errorLectura = fmt.Fscan(lector, &extra); errorLectura != io.EOF {
		return nil, fmt.Errorf("sobran datos en %s", ruta)
	}
	return datos, nil
}

func multiplicar(a, b, c []float64, n int) {
	for fila := 0; fila < n; fila++ {
		for columna := 0; columna < n; columna++ {
			suma := 0.0
			for paso := 0; paso < n; paso++ {
				suma += a[fila*n+paso] * b[paso*n+columna]
			}
			c[fila*n+columna] = suma
		}
	}
}

// validar revisa la suma total y tres celdas con el temporizador detenido.
func validar(c []float64, n int, control [4]float64) error {
	total := 0.0
	for _, valor := range c {
		total += valor
	}
	centro := (n/2)*n + n/2
	if total != control[0] || c[0] != control[1] || c[centro] != control[2] || c[len(c)-1] != control[3] {
		return fmt.Errorf("la multiplicación no pasó la validación")
	}
	return nil
}

func principal() error {
	runtime.GOMAXPROCS(1)

	// 1. Revisar el argumento y evitar mediciones duplicadas.
	if len(os.Args) != 2 || (os.Args[1] != "500" && os.Args[1] != "1000" && os.Args[1] != "1500") {
		return fmt.Errorf("uso: 01_entornos/bin/go.exe 500 (o 1000 o 1500)")
	}
	n, _ := strconv.Atoi(os.Args[1])
	carpeta := "03_crear matrices/" + strconv.Itoa(n) + "/"
	rutaSalida := "06_resultados/go.csv"
	cabecera := []string{"language", "N", "repetition", "time_seconds"}
	anterior, errorArchivo := os.Open(rutaSalida)
	nuevo := true
	if errorArchivo != nil && !os.IsNotExist(errorArchivo) {
		return errorArchivo
	}
	if errorArchivo == nil {
		filas, errorCSV := csv.NewReader(anterior).ReadAll()
		anterior.Close()
		if errorCSV != nil {
			return errorCSV
		}
		nuevo = len(filas) == 0
		if !nuevo && fmt.Sprint(filas[0]) != fmt.Sprint(cabecera) {
			return fmt.Errorf("el CSV tiene un encabezado diferente")
		}
		for posicion, fila := range filas {
			if posicion > 0 && len(fila) == 4 && fila[1] == strconv.Itoa(n) {
				return fmt.Errorf("este tamaño ya tiene filas; conserva los CSV antes de repetir")
			}
		}
	}
	// 2. Cargar las matrices y sus valores de control.
	a, errorArchivo := cargarMatriz(carpeta+"a.txt", n)
	if errorArchivo != nil {
		return errorArchivo
	}
	b, errorArchivo := cargarMatriz(carpeta+"b.txt", n)
	if errorArchivo != nil {
		return errorArchivo
	}
	referencia, errorArchivo := os.Open(carpeta + "control.txt")
	if errorArchivo != nil {
		return errorArchivo
	}
	var tamano int
	var control [4]float64
	_, errorArchivo = fmt.Fscan(referencia, &tamano, &control[0], &control[1], &control[2], &control[3])
	referencia.Close()
	if errorArchivo != nil || tamano != n {
		return fmt.Errorf("archivo de control incorrecto")
	}
	// 3. Preparar el archivo y la matriz de salida antes de medir.
	if errorArchivo = os.MkdirAll(filepath.Dir(rutaSalida), 0755); errorArchivo != nil {
		return errorArchivo
	}
	salida, errorArchivo := os.OpenFile(rutaSalida, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if errorArchivo != nil {
		return errorArchivo
	}
	defer salida.Close()
	escritor := csv.NewWriter(salida)
	if nuevo {
		if errorArchivo = escritor.Write(cabecera); errorArchivo != nil {
			return errorArchivo
		}
	}
	// C se reserva una vez y se sobrescribe completamente en cada producto.
	c := make([]float64, n*n)

	// 4. Excluir los calentamientos y guardar diez mediciones.
	for ejecucion := 1; ejecucion <= calentamientos+repeticiones; ejecucion++ {
		// Se mide únicamente la llamada a multiplicar.
		inicio := time.Now()
		multiplicar(a, b, c, n)
		fin := time.Now()
		segundos := fin.Sub(inicio).Seconds()
		if errorArchivo = validar(c, n, control); errorArchivo != nil {
			return errorArchivo
		}
		if ejecucion > calentamientos {
			repeticion := ejecucion - calentamientos
			fila := []string{"go", strconv.Itoa(n), strconv.Itoa(repeticion), fmt.Sprintf("%.9f", segundos)}
			if errorArchivo = escritor.Write(fila); errorArchivo != nil {
				return errorArchivo
			}
			escritor.Flush()
			if errorArchivo = escritor.Error(); errorArchivo != nil {
				return errorArchivo
			}
			fmt.Printf("go | N=%d | repetición=%d | %.9f s\n", n, repeticion, segundos)
		} else {
			fmt.Printf("go | N=%d | calentamiento %d/2\n", n, ejecucion)
		}
	}
	return nil
}

func main() {
	if errorPrograma := principal(); errorPrograma != nil {
		fmt.Fprintln(os.Stderr, "Error:", errorPrograma)
		os.Exit(1)
	}
}
