# TP N°2 - Desarrollo de Software

Este proyecto permite generar y cargar una gran cantidad de registros de alumnos en una base de datos PostgreSQL de forma eficiente. Está orientado a evaluar rendimiento, paralelización y manejo de archivos de gran tamaño

---

## 🧱 1. Clonar el repositorio

### 🔸 Si **NO** tenés Git instalado:

1. Descargá el repositorio desde:  
   👉 https://github.com/nicoandino/TP-N-2-Desarrollo-Nicolas-Andino.git  
2. Descomprimilo en la carpeta donde quieras trabajar.

### 🔹 Si **tenés Git** instalado:

git clone https://github.com/nicoandino/TP-N-2-Desarrollo-Nicolas-Andino.git
cd TP-N-2-Desarrollo-Nicolas-Andino

------
📦 2. Crear un entorno virtual (opcional pero recomendado)
# en Windows
python -m venv venv
venv\Scripts\activate.bat

# en Linux/macOS
python3 -m venv venv
source venv/bin/activate

------
📥 3. Instalar dependencias
pip install -r requirements.txt

------

🧾 Archivos principales
📌ACLARACION IMPORTANTE📌
El archivo no esta directamente en el repositorio porque tiene un tamaño aproximado de 140 MB
Crearlo antes de ejecutar el script principal o cargar si se tiene uno

"crear_csv.py"
Este script genera un archivo llamado alumnos.csv con 2.5 millones de registros de alumnos generados aleatoriamente, respetando ciertas condiciones definidas en el código.
Se creara y guardara en la raiz de la carpeta
DEMORA APROXIMADAMENTE 1 MINUTO

📌 Si querés cambiar la estructura, columnas o formato de los datos generados, modificá directamente el archivo "crear_csv.py".
▶️ Para ejecutarlo en consola:
Verifica: •En cmd estes en la ruta donde descomprimiste el repositorio y estan todos los archivos

en cmd ejecuta:
python crear_csv.py

📌Si ya contás con un archivo propio de alumnos en formato .csv, simplemente:
Renombralo como "alumnos.csv".
Ubicalo en la raíz del proyecto (es decir, en la misma carpeta donde clonaste este repositorio).

------

⚙️ Configuración del entorno
Antes de continuar, asegurate de tener configurado el archivo .env con tus datos de conexión a PostgreSQL:
SQLALCHEMY_DATABASE_URI=postgresql://usuario:contraseña@localhost:5432/dev_sysacad

------
📌🚀 Carga de datos
Una vez generado o ubicado el archivo alumnos.csv, ejecutá el script:
en cmd:
python insert_alumnos.py

Este archivo se encargará de insertar los registros en la base de datos utilizando paralelización y procesamiento por lotes para mejorar el rendimiento
📌IMPORTANTE📌
En la consola quizas le figurara que se carga en test_sysacad, pero se carga si o si en dev_sysacad 
------
⚡ Optimización
Si querés mejorar el tiempo de carga según tu CPU y memoria RAM disponible, podés modificar las siguientes líneas en insert_alumnos.py (líneas 20 y 21 aproximadamente):

BATCH_SIZE = 100_000   # Tamaño del lote de inserción
MAX_WORKERS = 6        # Cantidad de hilos en paralelo

Sugerencias:
Si tenés más RAM, podés subir BATCH_SIZE a 200_000
Si tenés más núcleos, podés subir MAX_WORKERS a 8 o 16.

------

Autor: Nicolas Andino
Legajo N° 9935
Tiempo alcanzado para la carga de alumnos : 23.73 segundos

Probado en :
Operating System: Windows 11 Pro 64-bit (10.0, Build 22631) (22621.ni_release.220506-1250)
Language: Spanish (Regional Setting: Spanish)
System Manufacturer: HP
System Model: HP Laptop 15-dy2xxx
BIOS: F.33 (type: UEFI)
Processor: 11th Gen Intel(R) Core(TM) i5-1135G7 @ 2.40GHz (8 CPUs), ~2.4GHz
Memory: 8192MB RAM
Available OS Memory: 7834MB RAM
