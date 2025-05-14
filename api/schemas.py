# api/schemas.py
from pydantic import BaseModel, Field, field_validator # field_validator para Pydantic v2 si es necesario
from typing import List, Optional
from datetime import datetime

# --- Esquemas de Producto (Product) ---
class ProductBaseAPI(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="Martillo de Uña Profesional")
    quantity_available: int = Field(..., ge=0, example=100)
    sale_price: float = Field(..., gt=0, example=25.50)
    purchase_price: float = Field(..., ge=0, example=12.75)

class ProductCreateAPI(ProductBaseAPI):
    pass

class ProductUpdateAPI(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, example="Martillo de Bola Reforzado")
    quantity_available: Optional[int] = Field(None, ge=0, example=90)
    sale_price: Optional[float] = Field(None, gt=0, example=26.00)
    purchase_price: Optional[float] = Field(None, ge=0, example=13.00)
    is_active: Optional[bool] = Field(None, example=True)

class ProductAPI(ProductBaseAPI):
    id: int
    is_active: bool

    # Configuración para Pydantic
    # Para Pydantic V2:
    model_config = {
        "from_attributes": True
    }
    # Para Pydantic V1 (si estás usando una versión más antigua):
    # class Config:
    #     orm_mode = True


# --- Esquemas de Venta (Sale) ---
class SaleItemCreateAPI(BaseModel):
    product_id: int = Field(..., example=1)
    quantity_sold: int = Field(..., gt=0, example=2)

class SaleCreateAPI(BaseModel):
    initial_cash: float = Field(..., ge=0, example=100000.0)
    items: List[SaleItemCreateAPI] = Field(..., min_length=1)

class SaleItemDetailAPI(BaseModel):
    product_id: int
    quantity_sold: int
    price_per_unit: float
    subtotal: float

    # Configuración para Pydantic
    model_config = {
        "from_attributes": True
    }
    # class Config:
    #     orm_mode = True

class SaleDetailAPI(BaseModel):
    id: int
    user_id: int
    sale_timestamp: datetime
    initial_cash: float
    total_amount: float
    items: List[SaleItemDetailAPI]

    # Configuración para Pydantic
    model_config = {
        "from_attributes": True
    }
    # class Config:
    #     orm_mode = True

class SaleCreationResponseAPI(BaseModel):
    id: int
    message: str = Field("Venta registrada exitosamente", example="Venta registrada exitosamente")
    total_amount_calculated: float = Field(..., example=51.00)