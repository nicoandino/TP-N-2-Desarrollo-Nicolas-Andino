import pandas as pd

input_csv = 'alumnos.csv'
output_csv = 'alumnos_limpio.csv'

df = pd.read_csv(input_csv)
# Limpiar espacios en blanco
for col in ['apellido', 'nombre', 'tipo_documento', 'sexo']:
    df[col] = df[col].str.strip()
# Optimizar tipos numéricos
df['nro_documento'] = pd.to_numeric(df['nro_documento'], downcast='integer')
df['nro_legajo'] = pd.to_numeric(df['nro_legajo'], downcast='integer')
# Guardar CSV limpio
df.to_csv(output_csv, index=False)
print(f"Limpieza completada: {input_csv} -> {output_csv}")