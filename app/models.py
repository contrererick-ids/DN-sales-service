from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(20), nullable=False, unique=True)
    cliente_id = Column(Integer, nullable=False)
    direccion_facturacion_id = Column(Integer, nullable=False)
    direccion_envio_id = Column(Integer, nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    fecha_creacion = Column(DateTime, server_default=func.now())

    contenido = relationship("ContenidoNota", back_populates="nota")


class ContenidoNota(Base):
    __tablename__ = "contenido_nota"

    id = Column(Integer, primary_key=True, index=True)
    nota_id = Column(Integer, ForeignKey("notas.id"), nullable=False)
    producto_id = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)
    importe = Column(DECIMAL(10, 2), nullable=False)

    nota = relationship("Nota", back_populates="contenido")
