from pydantic import BaseModel
from typing import List, Optional

class Producto(BaseModel):
    id: int
    nombre: str
    cantidad: float
    precio: float

class VentaItem(BaseModel):
    producto_id: int
    cantidad: float

class VentaCreate(BaseModel):
    items: List[VentaItem]
    base_inicial: float
    usuario_id: Optional[int] = 1

class Venta(BaseModel):
    id: int
    mensaje: str