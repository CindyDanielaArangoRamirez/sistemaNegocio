from fastapi import APIRouter, HTTPException, Depends
from typing import List
from .schemas import Producto, VentaCreate, Venta
from app.models.product_model import ProductModel
from app.models.sale_model import SaleModel

router = APIRouter()
product_model = ProductModel()
sale_model = SaleModel()

@router.get("/productos", response_model=List[Producto])
async def listar_productos():
    try:
        productos = product_model.get_all_products()
        return [{
            "id": p[0],
            "nombre": p[1],
            "cantidad": p[2],
            "precio": p[3]
        } for p in productos]
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/ventas", response_model=Venta)
async def crear_venta(venta: VentaCreate):
    try:
        items_db = [
            (item.producto_id, item.cantidad, 0, 0)
            for item in venta.items
        ]
        
        venta_id = sale_model.create_sale(
            usuario_id=1,
            base_inicial=venta.base_inicial,
            total=0,
            items=items_db
        )
        
        if venta_id:
            return {"id": venta_id, "mensaje": "Venta registrada"}
        raise HTTPException(400, "Error al crear venta")
    except Exception as e:
        raise HTTPException(500, str(e))