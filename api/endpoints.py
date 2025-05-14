# api/endpoints.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict
import sys
import os

try:
    from app.models.product_model import ProductModel
    from app.models.sale_model import SaleModel
except ImportError:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from app.models.product_model import ProductModel
    from app.models.sale_model import SaleModel

from . import schemas
# from .dependencies import verify_api_key # Descomentar para autenticación

router = APIRouter()
# router_authenticated = APIRouter(dependencies=[Depends(verify_api_key)]) # Para rutas autenticadas

# === PRODUCT ENDPOINTS ===
@router.post("/products/", response_model=schemas.ProductAPI, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo producto")
async def create_product_endpoint(product_data: schemas.ProductCreateAPI):
    product_id = ProductModel.add_product(
        name=product_data.name,
        quantity_available=product_data.quantity_available,
        sale_price=product_data.sale_price,
        purchase_price=product_data.purchase_price
    )
    if not product_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo crear el producto.")
    created_product_db = ProductModel.get_product_by_id(product_id)
    if not created_product_db:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Producto creado pero no se pudo recuperar.")
    return created_product_db # Pydantic convierte sqlite3.Row a ProductAPI

@router.get("/products/", response_model=List[schemas.ProductAPI], summary="Obtener lista de productos activos")
async def get_all_products_endpoint(skip: int = 0, limit: int = 100, include_inactive: bool = False):
    if include_inactive:
        # Necesitarías un método como ProductModel.get_all_including_inactive()
        # Por ahora, solo se devuelven activos
        products_db_rows = ProductModel.get_all_products()
    else:
        products_db_rows = ProductModel.get_all_products() # Ya filtra por activos
    
    if products_db_rows is None:
        return []
    return products_db_rows[skip : skip + limit]

@router.get("/products/{product_id}", response_model=schemas.ProductAPI, summary="Obtener un producto por su ID")
async def get_product_by_id_endpoint(product_id: int):
    product_db_row = ProductModel.get_product_by_id(product_id)
    if not product_db_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto con ID {product_id} no encontrado.")
    return product_db_row

@router.put("/products/{product_id}", response_model=schemas.ProductAPI, summary="Actualizar un producto existente")
async def update_product_endpoint(product_id: int, product_data: schemas.ProductUpdateAPI):
    existing_product_db = ProductModel.get_product_by_id(product_id)
    if not existing_product_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto con ID {product_id} no encontrado para actualizar.")

    update_data_payload = product_data.model_dump(exclude_unset=True)

    name_to_update = update_data_payload.get('name', existing_product_db['name'])
    qty_to_update = update_data_payload.get('quantity_available', existing_product_db['quantity_available'])
    sale_p_to_update = update_data_payload.get('sale_price', existing_product_db['sale_price'])
    purchase_p_to_update = update_data_payload.get('purchase_price', existing_product_db['purchase_price'])

    success = ProductModel.update_product(
        product_id=product_id,
        name=name_to_update,
        quantity_available=qty_to_update,
        sale_price=sale_p_to_update,
        purchase_price=purchase_p_to_update
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo actualizar el producto.")

    if 'is_active' in update_data_payload and update_data_payload['is_active'] is not None:
        if update_data_payload['is_active'] != existing_product_db['is_active']: # Solo actuar si hay cambio
            if update_data_payload['is_active']:
                ProductModel.restore_product(product_id)
            else:
                ProductModel.soft_delete_product(product_id)

    updated_product_db = ProductModel.get_product_by_id(product_id)
    return updated_product_db

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un producto (soft delete)")
async def delete_product_endpoint(product_id: int):
    existing_product_db = ProductModel.get_product_by_id(product_id)
    if not existing_product_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto con ID {product_id} no encontrado.")
    if not existing_product_db['is_active']:
        return
    success = ProductModel.soft_delete_product(product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo marcar el producto como inactivo.")
    return

# === SALE ENDPOINTS ===
@router.post("/sales/", response_model=schemas.SaleCreationResponseAPI, status_code=status.HTTP_201_CREATED, summary="Crear una nueva venta")
async def create_sale_endpoint(sale_data: schemas.SaleCreateAPI):
    user_id_for_sale = 1 # Hardcoded. Integrar autenticación para obtener el user_id real.
    items_for_model = []
    calculated_total_amount = 0.0

    if not sale_data.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La venta debe contener al menos un producto.")

    for item_api in sale_data.items:
        product_details = ProductModel.get_product_by_id(item_api.product_id)
        if not product_details or not product_details['is_active']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Producto con ID {item_api.product_id} no encontrado o está inactivo.")
        if item_api.quantity_sold <= 0:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"La cantidad vendida para el producto ID {item_api.product_id} debe ser mayor a cero.")
        if item_api.quantity_sold > product_details['quantity_available']:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Stock insuficiente para '{product_details['name']}' (ID: {item_api.product_id}). Disponibles: {product_details['quantity_available']}, Solicitados: {item_api.quantity_sold}")
        
        price_at_sale = product_details['sale_price']
        items_for_model.append({
            'product_id': item_api.product_id,
            'quantity_sold': item_api.quantity_sold,
            'price_per_unit': price_at_sale
        })
        calculated_total_amount += item_api.quantity_sold * price_at_sale
    
    sale_id_db = SaleModel.create_sale(
        user_id=user_id_for_sale,
        initial_cash=sale_data.initial_cash,
        total_amount=calculated_total_amount,
        items=items_for_model
    )
    if not sale_id_db:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al registrar la venta.")
    return schemas.SaleCreationResponseAPI(id=sale_id_db, total_amount_calculated=calculated_total_amount)