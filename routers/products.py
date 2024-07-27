from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, condecimal
from pymongo.collection import Collection
from bson.objectid import ObjectId
from datetime import datetime
from database import db


router = APIRouter()

collection: Collection = db["products"]

class Product(BaseModel):
    name: str
    price: float
    description: str

@router.get("/products/")
def read_products():
    products = collection.find()
    products_list = []
    for product in products:
        product["id"] = str(product["_id"])  
        del product["_id"]  
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


@router.post("/products/")
def create_product(product: Product):
    product_dict = product.dict()
    product_dict["created_at"] = datetime.utcnow()
    product_dict["updated_at"] = datetime.utcnow()

    result = collection.insert_one(product_dict)

    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Provider could not be created")
    
    return {"id": str(result.inserted_id)}


@router.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    old_product = collection.find_one({"_id": ObjectId(product_id)})

    if old_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product_dict = product.dict()
    
    product_dict["updated_at"] = datetime.utcnow()
    
    # Actualizar el proveedor en la colección
    result = collection.update_one({"_id": ObjectId(product_id)}, {"$set": product_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Product could not be updated")

    # Recuperar el documento actualizado
    updated_product = collection.find_one({"_id": ObjectId(product_id)})
    updated_product["id"] = str(updated_product["_id"])
    del updated_product["_id"]

    return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: str):
    product = collection.find_one({"_id": ObjectId(product_id)})

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    collection.delete_one({"_id": ObjectId(product_id)})
    return {"message": f"provider with the id '{product_id}' was deleted"}
