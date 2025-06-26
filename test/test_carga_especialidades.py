import os
import unittest
from sqlalchemy import text
from app import create_app, db

# Modelo actualizado
class EspecialidadModel(db.Model):
    __tablename__ = 'especialidades'
    id = db.Column(db.Integer, primary_key=True)
    especialidad = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    observacion = db.Column(db.String(255), nullable=True)

class InsertManualTestCase(unittest.TestCase):

    def setUp(self):
        # Variables de entorno
        os.environ['FLASK_CONTEXT'] = 'testing'
        os.environ['TEST_DATABASE_URI'] = 'postgresql+psycopg2://nico:nico@localhost:5432/test_sysacad'

        # Crear app y contexto
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Resetear DB
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_manual_insert(self):
        # Crear un objeto de prueba
        nueva_especialidad = EspecialidadModel(
            especialidad=9999,
            nombre='PRUEBA DE INSERCIÓN',
            observacion='Este es un test manual.'
        )

        # Insertar y confirmar
        db.session.add(nueva_especialidad)
        db.session.commit()

        # Verificar que se insertó
        resultado = EspecialidadModel.query.filter_by(especialidad=9999).first()
        self.assertIsNotNone(resultado, "No se insertó la especialidad.")
        print(f"✅ Insertado: {resultado.nombre} con ID {resultado.id}")

if __name__ == '__main__':
    unittest.main()
