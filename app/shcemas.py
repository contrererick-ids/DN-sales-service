from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ContenidoNotaBase(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float

class ContenidoNotaCreate(ContenidoNotaBase):
    pass

class ContenidoNotaResponse(ContenidoNotaBase):
    id: int
    importe: float

    class Config:
        from_attributes = True


class NotaBase(BaseModel):
    cliente_id: int
    direccion_facturacion_id: int
    direccion_envio_id: int

class NotaCreate(NotaBase):
    contenido: List[ContenidoNotaCreate]

class NotaResponse(NotaBase):
    id: int
    folio: str
    total: float
    fecha_creacion: Optional[datetime]
    contenido: List[ContenidoNotaResponse] = []

    class Config:
        from_attributes = True
