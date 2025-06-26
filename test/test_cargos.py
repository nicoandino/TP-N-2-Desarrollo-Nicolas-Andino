import os
import unittest
from sqlalchemy import text
from app import create_app, db
from xml.etree import ElementTree as ET

# Modelo actualizado
class GradoModel(db.Model):
    __tablename__ = 'grados'
    id = db.Column(db.Integer, primary_key=True)
    grado = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)

class XMLImportTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        os.environ['TEST_DATABASE_URI'] = 'postgresql+psycopg2://matuu:matu@localhost:5432/test_sysacad'

        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()  # Limpia la base de datos antes de crear las tablas
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_import_xml_to_db(self):
        # Ruta del archivo XML
        xml_file_path = os.path.join(
            os.path.dirname(__file__), '..', 'archivados_xml', 'grados.xml'
        )

        # Verificamos que el archivo exista
        self.assertTrue(os.path.exists(xml_file_path), f"El archivo {xml_file_path} no existe.")

        
        # Parseamos el archivo XML
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        for item in root.findall('_expxml'):
            grado_element = item.find('grado')
            nombre_element = item.find('nombre')

            # Aseguramos que los elementos requeridos no sean None
            if grado_element is not None and nombre_element is not None:
                try:
                    grado = int(grado_element.text.strip())
                    nombre = nombre_element.text.strip()

                    # Insertamos en la base de datos
                    new_entry = GradoModel(
                        grado=grado,
                        nombre=nombre
                    )
                    db.session.add(new_entry)
                except ValueError:
                    print(f"Error: No se pudo convertir el grado '{grado_element.text}' a número entero")
            else:
                print(f"skipeo el item por que falta algun dato. Grado: {grado_element}, "
                        f"Nombre: {nombre_element}")

            db.session.commit()

            # Verificamos que los datos se hayan insertado correctamente
            results = GradoModel.query.all()
            self.assertGreater(len(results), 0, "No se insertaron datos en la base de datos.")
            for result in results:
                print(f"Grado: {result.grado}, Nombre: {result.nombre}")

if __name__ == '__main__':
    unittest.main()