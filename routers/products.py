from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, condecimal
from pymongo.collection import Collection
from bson.objectid import ObjectId
from datetime import datetime
from database import db
from typing import List


router = APIRouter()

collection: Collection = db["products"]
provider_collection: Collection = db["providers"]

class Product(BaseModel):
    name: str
    price: float
    description: str
    provider_id: str


@router.get("/products")
def read_products(
    limit: int = Query(10, gt=0, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    name: str = Query(None, description="Filter by product name")
):
    # Construir el filtro de consulta
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}  # Búsqueda insensible a mayúsculas/minúsculas

    # Aplicar filtros y parámetros de paginación
    products = collection.find(query).skip(offset).limit(limit)
    products_list = []
    for product in products:
        # Convertir ObjectId a cadena para id y provider_id
        product["id"] = str(product["_id"])  
        del product["_id"]
        if "provider_id" in product:
            product["provider_id"] = str(product["provider_id"])
        
        products_list.append(product)

    if not products_list:
        raise HTTPException(status_code=404, detail="No products found")
    
    return products_list

@router.get("/products/{product_id}")
def read_product(product_id: str):
    product = collection.find_one({"_id": ObjectId(product_id)})

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product["id"] = str(product["_id"])  
    del product["_id"]  
    return product


@router.post("/products")
def create_product(product: Product):
    provider = provider_collection.find_one({"_id": ObjectId(product.provider_id)})
    if provider is None:
        raise HTTPException(status_code=400, detail="Provider ID does not exist")
    
    product_dict = product.dict()
    product_dict["created_at"] = datetime.utcnow()
    product_dict["updated_at"] = datetime.utcnow()
    product_dict["provider_id"] = ObjectId(product.provider_id)
    

    result = collection.insert_one(product_dict)

    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Product could not be created")
    
    
    return {"id": str(result.inserted_id)}

@router.post("/products/multiple")
def create_products(products: List[Product]):
    products_dict = []
    for product in products:
        product_dict = product.dict()
        product_dict["created_at"] = datetime.utcnow()
        product_dict["updated_at"] = datetime.utcnow()
        products_dict.append(product_dict)

    result = collection.insert_many(products_dict)

    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Providers could not be created")

    return {"ids": [str(inserted_id) for inserted_id in result.inserted_ids]}


@router.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    old_product = collection.find_one({"_id": ObjectId(product_id)})

    if old_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verificar si el provider_id existe en la colección providers
    provider = provider_collection.find_one({"_id": ObjectId(product.provider_id)})
    if provider is None:
        raise HTTPException(status_code=400, detail="Provider ID does not exist")

    product_dict = product.dict()
    product_dict["updated_at"] = datetime.utcnow()
    product_dict["provider_id"] = ObjectId(product.provider_id)
    
    # Actualizar el proveedor en la colección
    result = collection.update_one({"_id": ObjectId(product_id)}, {"$set": product_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Product could not be updated")

    # Recuperar el documento actualizado
    updated_product = collection.find_one({"_id": ObjectId(product_id)})
    updated_product["id"] = str(updated_product["_id"])
    updated_product["provider_id"] = str(updated_product["provider_id"])
    del updated_product["_id"]

    return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: str):
    product = collection.find_one({"_id": ObjectId(product_id)})

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    collection.delete_one({"_id": ObjectId(product_id)})
    return {"message": f"provider with the id '{product_id}' was deleted"}
