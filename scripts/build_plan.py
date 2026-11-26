#!/usr/bin/env python3
"""
Arma plan.csv: qué fotos entran al video y en qué orden.

Datos de entrada: ESTIMACIONES por foto, cargadas a mano después de mirar las 210 fotos.
  (n° de foto en orden alfabético de la carpeta) -> (edad estimada, calidad)
  calidad: 3 = foto individual clara, 2 = aceptable, 1 = foto grupal/débil, 0 = descartar

Uso:  python3 scripts/build_plan.py          (corre desde la raíz del repo)
Para ajustar el video: tocar N_POR_ALUMNO o las estimaciones y volver a correr.
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N_POR_ALUMNO = 8  # máximo de fotos por alumno (los que tienen menos usan todas las que tienen)

# carpeta -> nombre según listado oficial
ALUMNOS = {
    "Bogan Julian": "BOGAN, Julián",
    "Calcena Martina": "CÁLCENA, Martina Belén",
    "Chacana Bhianca": "CHACANA, Bhianca Aylén",
    "Delgado Valentina": "DELGADO, Valentina Lucía",
    "Della Savia Mateo": "DELLA SAVIA, Mateo",
    "Garcia Diana Juan Ignacio": "GARCÍA DIANA, Juan Martín",
    "Gonzalez Pitronacci Alegra": "GONZALEZ PITRONACI, Allegra Simona",
    "Libertini Luca": "LIBERTINI, Luca",
    "Mognoni Nicolas": "MOGNONI, Nicolás Augusto",
    "Ocampos": "OCAMPOS, Matías",
    "Paloma Fontan Rama": "FONTAN RAMA, Paloma Sofía",
    "Perrone Franco": "PERRONE, Franco",
    "Robledo Coria Bautista": "ROBLEDO CORIA, Bautista Nicolas",
    "Sabatte Anna": "SABATTE, Anna",
    "Schauffele Felipe": "SCHAUFFELE, Felipe",
    "Silva, Santino": "SILVA, Santino León",
    "Velletri Liezel": "VELLETRI CUBILLA, Liezel Brielle",
}

# carpeta -> {n° de foto (orden alfabético): (edad estimada, calidad)}
EDADES = {
    "Bogan Julian": {1: (10, 3), 2: (5, 3), 3: (5, 3), 4: (7, 1), 5: (7, 3), 6: (7, 3),
                     7: (7, 3), 8: (7, 1), 9: (9, 3), 10: (11, 3), 11: (11.5, 2)},
    "Calcena Martina": {1: (4, 3), 2: (13, 3), 3: (3, 3), 4: (6, 3), 5: (3, 1), 6: (5, 3),
                        7: (8.5, 3), 8: (7, 3), 9: (10.5, 3), 10: (10, 3)},
    "Chacana Bhianca": {1: (10.5, 2), 2: (9, 1), 3: (12, 1), 4: (10, 3), 5: (9, 3),
                        6: (8, 2), 7: (10.5, 1), 8: (10, 3)},
    "Delgado Valentina": {1: (2.5, 3), 2: (13, 3), 3: (4.5, 3), 4: (5, 3), 5: (5.5, 3),
                          6: (7, 3), 7: (6, 3), 8: (8, 3), 9: (11, 2), 10: (12, 3)},
    "Della Savia Mateo": {1: (2.5, 3), 2: (4, 3), 3: (5, 3), 4: (5.5, 3), 5: (7, 3),
                          6: (6, 3), 7: (9, 3), 8: (12, 3)},
    "Garcia Diana Juan Ignacio": {1: (12, 1), 2: (11, 1), 3: (11, 2), 4: (9, 3), 5: (8, 3),
                                  6: (7, 3), 7: (6.5, 3), 8: (6, 3), 9: (6, 2), 10: (5, 1),
                                  11: (5, 2), 12: (6.5, 3), 13: (11, 3), 14: (11, 2),
                                  15: (10.5, 3), 16: (11, 2), 17: (10, 3), 18: (12, 3)},
    "Gonzalez Pitronacci Alegra": {1: (5, 3), 2: (5, 3), 3: (3, 3), 4: (12, 2), 5: (5, 2),
                                   6: (10.5, 2), 7: (10.5, 1), 8: (5, 3), 9: (4, 3),
                                   10: (12, 3), 11: (12, 2), 12: (13, 3), 13: (4, 3),
                                   14: (12, 3)},
    "Libertini Luca": {1: (2, 3), 2: (13, 2), 3: (3.5, 3), 4: (5, 3), 5: (4, 3), 6: (5.5, 3),
                       7: (5.5, 2), 8: (9, 3), 9: (10.5, 3), 10: (10.5, 1)},
    "Mognoni Nicolas": {1: (9, 2), 2: (9, 2), 3: (11, 1), 4: (9, 2), 5: (9, 2), 6: (8, 2),
                        7: (11, 2), 8: (11, 1), 9: (11, 3), 10: (9, 1), 11: (10, 2),
                        12: (11, 3), 13: (11, 2), 14: (10, 2), 15: (12, 3), 16: (9, 2),
                        17: (12, 2)},
    "Ocampos": {1: (11, 2), 2: (11, 1), 3: (10.5, 3), 4: (8, 1), 5: (7, 2), 6: (6.5, 3),
                7: (3.5, 3), 8: (5, 3), 9: (5.5, 2), 10: (4, 3),
                11: (10.5, 3)},  # 11 = "Mateo 7.png": es de Della Savia (ver FOTOS_MAL_UBICADAS)
    "Paloma Fontan Rama": {1: (12, 2), 2: (13, 3), 3: (12.5, 3), 4: (13, 2), 5: (11, 3),
                           6: (11, 3), 7: (10, 2), 8: (12, 2), 9: (12, 1), 10: (12, 2),
                           11: (10, 3), 12: (10, 3), 13: (10.5, 3), 14: (10.5, 3), 15: (10, 2),
                           16: (10, 2), 17: (9, 2), 18: (8, 3), 19: (8, 1), 20: (7.5, 2),
                           21: (8, 3), 22: (7, 3), 23: (7.5, 1), 24: (7.5, 2), 25: (3.5, 3),
                           26: (4, 0)},  # 26 = dibujo hecho por ella, no es foto
    "Perrone Franco": {1: (10, 3), 2: (13, 2), 3: (2.5, 3), 4: (3.5, 3), 5: (5, 2),
                       6: (5, 3), 7: (5, 1), 8: (5, 3), 9: (5.5, 3),
                       10: (5, 0)},  # 10 = "Juan Martín S (6)": sin confirmar que sea Franco
    "Robledo Coria Bautista": {1: (8, 2), 2: (6, 1), 3: (8, 2), 4: (6, 0), 5: (13, 2),
                               6: (13, 3), 7: (13, 2)},  # 4 = recorte repetido de la 2
    "Sabatte Anna": {1: (6, 3), 2: (5, 3), 3: (8, 3), 4: (13, 3)},
    "Schauffele Felipe": {1: (12, 1), 2: (11, 1), 3: (11, 2), 4: (10, 1), 5: (9, 2),
                          6: (6, 3), 7: (12, 2), 8: (11, 2), 9: (10, 2), 10: (6, 3),
                          11: (10, 2), 12: (12, 1), 13: (12, 1), 14: (11, 2), 15: (11, 3),
                          16: (6, 3), 17: (6, 3), 18: (6, 2), 19: (10, 3), 20: (11, 1)},
    "Silva, Santino": {1: (11, 3), 2: (11, 3), 3: (11, 1), 4: (11, 2), 5: (11, 1), 6: (11.5, 2),
                       7: (12, 1), 8: (12, 1), 9: (12, 1), 10: (12, 3), 11: (13, 1),
                       12: (13, 2), 13: (13, 1)},
    "Velletri Liezel": {1: (5, 3), 2: (6, 2), 3: (10.5, 2), 4: (11, 3), 5: (7, 3), 6: (6, 3),
                        7: (6, 3), 8: (5, 3), 9: (5, 2), 10: (4, 1), 11: (5, 2), 12: (7, 3),
                        13: (5, 1)},
}

# Fotos que están en la carpeta de otro alumno (carpeta, archivo) -> carpeta real
FOTOS_MAL_UBICADAS = {("Ocampos", "Mateo 7.png"): "Della Savia Mateo"}
EDAD_MAL_UBICADAS = {("Ocampos", "Mateo 7.png"): (10.5, 3)}


def etapa(edad):
    if edad < 4:
        return "1-bebé / primeros años"
    if edad < 6.5:
        return "2-jardín / sala de 5"
    if edad < 10:
        return "3-primaria"
    if edad < 12:
        return "4-fin de primaria"
    return "5-secundaria / actualidad"


def elegir(cands, n):
    """Elige n fotos repartidas parejo a lo largo de las edades (cands ordenado por edad)."""
    buenas = [c for c in cands if c["q"] >= 2]
    pool = buenas if len(buenas) >= n else cands
    if len(pool) <= n:
        return pool
    idx = sorted({round(i * (len(pool) - 1) / (n - 1)) for i in range(n)})
    elegidas = [pool[i] for i in idx]
    # si el redondeo repitió posiciones, completa con las mejores restantes
    resto = sorted((c for c in pool if c not in elegidas), key=lambda c: -c["q"])
    while len(elegidas) < n and resto:
        elegidas.append(resto.pop(0))
    return sorted(elegidas, key=lambda c: c["edad"])


def main():
    por_alumno = {c: [] for c in ALUMNOS}
    for carpeta, fotos in EDADES.items():
        archivos = sorted(os.listdir(os.path.join(ROOT, carpeta)))
        assert len(archivos) == len(fotos), f"{carpeta}: {len(archivos)} archivos vs {len(fotos)} datos"
        for i, archivo in enumerate(archivos, start=1):
            edad, q = fotos[i]
            dueno = FOTOS_MAL_UBICADAS.get((carpeta, archivo), carpeta)
            if (carpeta, archivo) in EDAD_MAL_UBICADAS:
                edad, q = EDAD_MAL_UBICADAS[(carpeta, archivo)]
            if q == 0:
                continue
            por_alumno[dueno].append({"carpeta": carpeta, "archivo": archivo, "edad": edad,
                                      "q": q, "alumno": dueno})
    seleccion = []
    for carpeta, cands in por_alumno.items():
        cands = sorted(cands, key=lambda c: c["edad"])
        seleccion += elegir(cands, N_POR_ALUMNO)

    # Orden global: de más chicos a más grandes; desempata alternando alumnos
    seleccion.sort(key=lambda c: (c["edad"], c["alumno"]))
    # evita dos fotos seguidas del mismo alumno si hay otra cerca para intercambiar
    for i in range(1, len(seleccion)):
        if seleccion[i]["alumno"] == seleccion[i - 1]["alumno"]:
            for j in range(i + 1, min(i + 6, len(seleccion))):
                if seleccion[j]["alumno"] != seleccion[i - 1]["alumno"] and \
                        abs(seleccion[j]["edad"] - seleccion[i]["edad"]) <= 1.0:
                    seleccion[i], seleccion[j] = seleccion[j], seleccion[i]
                    break

    with open(os.path.join(ROOT, "plan.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["orden", "alumno", "archivo", "edad_estimada", "etapa"])
        for n, c in enumerate(seleccion, start=1):
            w.writerow([n, ALUMNOS[c["alumno"]], f'{c["carpeta"]}/{c["archivo"]}',
                        c["edad"], etapa(c["edad"])])

    # resumen
    print(f"Total de fotos en el video: {len(seleccion)}")
    cuenta = {}
    for c in seleccion:
        cuenta[c["alumno"]] = cuenta.get(c["alumno"], 0) + 1
    for k, v in sorted(cuenta.items(), key=lambda kv: kv[1]):
        print(f"  {ALUMNOS[k]:40} {v}")


if __name__ == "__main__":
    main()
