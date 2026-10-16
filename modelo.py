import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///pasteleria.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Pedido(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cliente = db.Column(
        db.String(100),
        nullable=False
    )

    tipo_pastel = db.Column(
        db.String(100),
        nullable=False
    )

    porciones = db.Column(
        db.Integer,
        nullable=False
    )

    decoracion = db.Column(
        db.String(150),
        nullable=False
    )

    fecha_entrega = db.Column(
        db.String(10),
        nullable=False
    )

    hora_entrega = db.Column(
        db.String(10),
        nullable=False
    )

    tiempo_preparacion = db.Column(
        db.Integer,
        nullable=False
    )

    estado = db.Column(
        db.String(30),
        nullable=False,
        default="pendiente"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente,
            "tipoPastel": self.tipo_pastel,
            "porciones": self.porciones,
            "decoracion": self.decoracion,
            "fechaEntrega": self.fecha_entrega,
            "horaEntrega": self.hora_entrega,
            "tiempoPreparacion": self.tiempo_preparacion,
            "estado": self.estado
        }


with app.app_context():
    db.create_all()