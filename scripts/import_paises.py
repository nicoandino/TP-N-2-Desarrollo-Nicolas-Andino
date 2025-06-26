import sys
import os
import locale

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)



from app import create_app, db
from xml.etree import ElementTree as ET
from sqlalchemy.exc import IntegrityError
from dataclasses import dataclass

# función para decodificar texto de windows-1252 a utf-8
def decode_win1252(text):
    if text is None:
        return None
    return text.encode('latin1').decode('windows-1252').encode('utf-8').decode('utf-8')

@dataclass(init=False, repr=True, eq=True)
class Pais(db.Model):
    __tablename__ = 'paises'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nombre = db.Column(db.String(100), nullable=False)

def importar_paises():
    """
    importa registros de países desde un XML codificado en Windows-1252,
    usando decode_win1252 para convertir cada texto a UTF-8.
    """
    os.environ['FLASK_CONTEXT'] = 'development'
    app = create_app()
    with app.app_context():
        db.create_all()

        xml_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'archivados_xml', 'paises.xml')
        )
        if not os.path.exists(xml_file_path):
            print(f"ERROR: no se encontró el archivo XML: {xml_file_path}")
            return

        print(f"Importando desde: {xml_file_path}")
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Error al parsear el archivo XML: {e}")
            return

        registros_importados = 0
        registros_duplicados = 0
        registros_error = 0

        for item in root.findall('_expxml'):
            pais_element = item.find('pais')
            nombre_element = item.find('nombre')

            if pais_element is not None and nombre_element is not None:
                try:
                    # decodificar antes de convertir a int, en caso de caracteres en Windows-1252
                    pais_id_text = decode_win1252(pais_element.text)
                    pais_id = int(pais_id_text)
                    nombre = decode_win1252(nombre_element.text)

                    existing = Pais.query.get(pais_id)
                    if existing:
                        print(f"Registro duplicado ID {pais_id}: {nombre}")
                        registros_duplicados += 1
                        continue

                    new_entry = Pais(
                        id=pais_id,
                        nombre=nombre
                    )
                    db.session.add(new_entry)
                    db.session.commit()
                    registros_importados += 1

                except ValueError:
                    db.session.rollback()
                    print(f"Error: el valor de país no es un número válido: {pais_element.text}")
                    registros_error += 1
                except IntegrityError:
                    db.session.rollback()
                    print(f"Error de integridad al insertar país {pais_id}")
                    registros_error += 1
                except Exception as e:
                    db.session.rollback()
                    # ET.tostring puede devolver cadenas con caracteres especiales, pero aquí se imprimen tal cual
                    print(f"Error al procesar item: {ET.tostring(item, encoding='unicode')}\n{e}")
                    registros_error += 1
            else:
                print(f"Skipeado por datos faltantes: {ET.tostring(item, encoding='unicode')}")
                registros_error += 1

        print(f"""
Importación finalizada:
- Registros insertados: {registros_importados}
- Registros duplicados: {registros_duplicados}
- Registros con error: {registros_error}
""")

if __name__ == '__main__':
    importar_paises()
