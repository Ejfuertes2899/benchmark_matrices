from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.graphics.gofplots import qqplot
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd


salida = Path(snakemake.output[0]).parent
salida.mkdir(parents=True, exist_ok=True)

alpha = float(snakemake.params.alpha)
lenguajes = ["cpp", "go", "java", "python"]
tamanos = [500, 1000, 1500]

datos = pd.read_csv(snakemake.input[0])
datos["log_time"] = np.log(datos["time_seconds"])

# 1. Estadística descriptiva en segundos.
descriptivos = (
    datos.groupby(["language", "N"])["time_seconds"]
    .agg(
        n="count",
        media="mean",
        mediana="median",
        desviacion="std",
        minimo="min",
        maximo="max",
    )
    .reset_index()
)

descriptivos.to_csv(
    salida / "descriptivos.csv", index=False
)

# 2. Modelos factoriales completos.
modelos = {
    "segundos": ols(
        "time_seconds ~ C(language) * C(N)",
        data=datos,
    ).fit(),
    "log": ols(
        "log_time ~ C(language) * C(N)",
        data=datos,
    ).fit(),
}

tablas_anova = {
    nombre: anova_lm(modelo, typ=2)
    for nombre, modelo in modelos.items()
}

tablas_anova["segundos"].to_csv(
    salida / "anova.csv", index_label="efecto"
)
tablas_anova["log"].to_csv(
    salida / "anova_log.csv", index_label="efecto"
)

# 3. Diagnósticos de ambos modelos.
diagnosticos = []

for nombre, variable in [
    ("segundos", "time_seconds"),
    ("log", "log_time"),
]:
    modelo = modelos[nombre]

    grupos = [
        grupo[variable].to_numpy()
        for _, grupo in datos.groupby(["language", "N"])
    ]

    diagnosticos.append({
        "modelo": nombre,
        "shapiro_p": float(
            stats.shapiro(modelo.resid).pvalue
        ),
        "levene_p": float(
            stats.levene(
                *grupos, center="median"
            ).pvalue
        ),
    })

supuestos = pd.DataFrame(diagnosticos)
supuestos.to_csv(
    salida / "supuestos.csv", index=False
)

# 4. Tukey del modelo principal sobre log(tiempo).
diagnostico_log = (
    supuestos.set_index("modelo").loc["log"]
)

significativo = (
    tablas_anova["log"]["PR(>F)"].dropna() < alpha
).any()

diagnosticos_sin_alerta = (
    diagnostico_log["shapiro_p"] >= alpha
    and diagnostico_log["levene_p"] >= alpha
)

columnas_tukey = [
    "group1", "group2", "meandiff",
    "p-adj", "lower", "upper", "reject",
]
tabla_tukey = pd.DataFrame(columns=columnas_tukey)

if not significativo:
    estado_tukey = (
        "No se ejecutó Tukey: el ANOVA principal "
        "no detectó efectos significativos."
    )
elif not diagnosticos_sin_alerta:
    estado_tukey = (
        "No se ejecutó Tukey: los diagnósticos del "
        "modelo principal detectan problemas. "
        "Revisar supuestos y gráficos antes de "
        "formular conclusiones inferenciales."
    )
else:
    etiquetas = (
        datos["language"]
        + "_N"
        + datos["N"].astype(str)
    )

    resultado = pairwise_tukeyhsd(
        endog=datos["log_time"],
        groups=etiquetas,
        alpha=alpha,
    )

    tabla = resultado.summary().data
    tabla_tukey = pd.DataFrame(
        tabla[1:], columns=tabla[0]
    )

    estado_tukey = (
        "Tukey ejecutado sobre log(tiempo), "
        "comparando las 12 combinaciones. "
        "Revisar también gráficos e independencia."
    )

tabla_tukey.to_csv(
    salida / "tukey.csv", index=False
)

# 5. Distribución de los tiempos por tamaño.
figura, ejes = plt.subplots(
    1, 3, figsize=(13, 4), sharey=True
)

for eje, n in zip(ejes, tamanos):
    muestras = [
        datos.loc[
            (datos["language"] == lenguaje)
            & (datos["N"] == n),
            "time_seconds",
        ].to_numpy()
        for lenguaje in lenguajes
    ]

    eje.boxplot(muestras)
    eje.set_xticks(range(1, 5))
    eje.set_xticklabels(lenguajes)
    eje.set_title(f"N = {n}")
    eje.set_yscale("log")
    eje.set_xlabel("Lenguaje")
    eje.grid(axis="y", alpha=0.3)

ejes[0].set_ylabel(
    "Tiempo en segundos — escala logarítmica"
)
figura.tight_layout()
figura.savefig(salida / "cajas.png", dpi=180)
plt.close(figura)

# 6. Gráficos de interacción en las dos escalas.
figura, ejes = plt.subplots(1, 2, figsize=(12, 4))

for eje, variable, etiqueta in [
    (ejes[0], "time_seconds", "Media del tiempo (s)"),
    (ejes[1], "log_time", "Media de log(tiempo)"),
]:
    for lenguaje in lenguajes:
        medias = (
            datos.loc[datos["language"] == lenguaje]
            .groupby("N")[variable]
            .mean()
            .reindex(tamanos)
        )
        eje.plot(
            tamanos, medias,
            marker="o", label=lenguaje,
        )

    eje.set_xticks(tamanos)
    eje.set_xlabel("Tamaño N")
    eje.set_ylabel(etiqueta)
    eje.grid(alpha=0.3)
    eje.legend()

figura.tight_layout()
figura.savefig(salida / "interaccion.png", dpi=180)
plt.close(figura)

# 7. Residuos y Q-Q para ambos modelos.
figura, ejes = plt.subplots(2, 2, figsize=(10, 8))

for fila, nombre in enumerate(["segundos", "log"]):
    modelo = modelos[nombre]

    ejes[fila, 0].scatter(
        modelo.fittedvalues,
        modelo.resid,
        alpha=0.7,
    )
    ejes[fila, 0].axhline(
        0, color="black", linestyle="--"
    )
    ejes[fila, 0].set_xlabel("Valor ajustado")
    ejes[fila, 0].set_ylabel("Residuo")
    ejes[fila, 0].set_title(
        f"Residuos: {nombre}"
    )

    qqplot(
        modelo.resid,
        line="s",
        ax=ejes[fila, 1],
    )
    ejes[fila, 1].set_title(f"Q-Q: {nombre}")

figura.tight_layout()
figura.savefig(salida / "diagnostico.png", dpi=180)
plt.close(figura)

# 8. Resumen para facilitar la revisión.
lineas = [
    "Diseño: 4 lenguajes x 3 tamaños x 10 repeticiones.",
    "Total: 120 mediciones.",
    f"Nivel de significación: {alpha}.",
    "Modelo principal: log_time ~ C(language) * C(N).",
    "El ANOVA en segundos se entrega como referencia.",
    "",
    "Valores p del modelo principal:",
]

for efecto in [
    "C(language)",
    "C(N)",
    "C(language):C(N)",
]:
    p = tablas_anova["log"].loc[efecto, "PR(>F)"]
    lineas.append(f"{efecto}: p = {p:.6g}")

lineas.extend([
    "",
    estado_tukey,
    "",
    "Si la interacción es significativa, interpretar "
    "las diferencias entre lenguajes para cada tamaño.",
    "Los diagnósticos no demuestran los supuestos.",
    "La independencia se evalúa mediante el diseño "
    "y las condiciones de ejecución.",
    "Son repeticiones técnicas sobre matrices fijas; "
    "las conclusiones se limitan al experimento medido.",
])

(salida / "resumen.txt").write_text(
    "\n".join(lineas) + "\n",
    encoding="utf-8",
)

print("Análisis, tablas y gráficos generados.")
