from app import db

class Alumnos(db.Model):
    __tablename__ = 'alumnos'
    apellido         = db.Column(db.String(255), nullable=False)
    nombre           = db.Column(db.String(255), nullable=False)
    nro_documento    = db.Column(db.Integer, nullable=False)
    tipo_documento   = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    sexo             = db.Column(db.String(1), nullable=False)
    nro_legajo       = db.Column(db.Integer, primary_key=True)
    fecha_ingreso    = db.Column(db.Date, nullable=False)
