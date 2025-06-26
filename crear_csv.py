import csv
import random
from datetime import datetime, timedelta
print("Generando archivo CSV de alumnos")
print("Demora aprox 1 minuto")
# Cantidad de registros a generar
N = 2_500_000

# Listas de ejemplo para nombres y apellidos
apellidos = [
    "Gonzalez", "Rodriguez", "Perez", "Martinez", "Gomez",
    "Esponjoso", "Williams"
]
nombres = [
    "Vals", "Juan", "Ana", "Luis", "Lucia","Tito"
]

tipos_documento = ["DNI"]
sexos = ["M", "F"]

# Rango de fechas para nacimiento (1940-01-01 a 2005-12-31)
fecha_nac_inicio = datetime(1940, 1, 1)
fecha_nac_fin = datetime(2005, 12, 31)
delta_nac = (fecha_nac_fin - fecha_nac_inicio).days

# Rango de fechas para ingreso (2000-01-01 a hoy)
hoy = datetime.today()
fecha_ing_inicio = datetime(2000, 1, 1)
delta_ing = (hoy - fecha_ing_inicio).days

with open('alumnos.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Escribimos el encabezado
    writer.writerow([
        'apellido',
        'nombre',
        'nro_documento',
        'tipo_documento',
        'fecha_nacimiento',
        'sexo',
        'nro_legajo',
        'fecha_ingreso'
    ])

    for legajo in range(1, N + 1):
        apellido = random.choice(apellidos)
        nombre = random.choice(nombres)

        # Documento: número aleatorio de 8 dígitos
        nro_documento = random.randint(10_000_000, 99_999_999)
        tipo_documento = random.choice(tipos_documento)

        # Fecha de nacimiento
        nac_offset = random.randint(0, delta_nac)
        fecha_nacimiento = fecha_nac_inicio + timedelta(days=nac_offset)
        fecha_nacimiento_str = fecha_nacimiento.strftime('%Y-%m-%d')

        # Sexo en función del nombre (simple heurístico)
        sexo = "F" if nombre.endswith(("a", "e", "á", "é")) else random.choice(sexos)

        # Fecha de ingreso
        ing_offset = random.randint(0, delta_ing)
        fecha_ingreso = fecha_ing_inicio + timedelta(days=ing_offset)
        fecha_ingreso_str = fecha_ingreso.strftime('%Y-%m-%d')

        writer.writerow([
            apellido,
            nombre,
            nro_documento,
            tipo_documento,
            fecha_nacimiento_str,
            sexo,
            legajo,
            fecha_ingreso_str
        ])

print(f"Archivo 'alumnos.csv' generado con {N} registros.")
