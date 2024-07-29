from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pymongo.collection import Collection
from bson.objectid import ObjectId
from datetime import datetime
from database import db
from typing import List

router = APIRouter()

collection: Collection = db["providers"]

class Provider(BaseModel):
    name: str
    address: str
    phone: str
    description: str

@router.get("/providers")
def read_providers(
    limit: int = Query(10, gt=0, description="Number of providers to return"),
    offset: int = Query(0, ge=0, description="Number of providers to skip"),
    name: str = Query(None, description="Filter by provider name")
):
    # Construir el filtro de consulta
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}  # Búsqueda insensible a mayúsculas/minúsculas

    # Aplicar filtros y parámetros de paginación
    providers = collection.find(query).skip(offset).limit(limit)
    providers_list = []
    for provider in providers:
        # Convertir ObjectId a cadena para id y provider_id
        provider["id"] = str(provider["_id"])  
        del provider["_id"]
        
        providers_list.append(provider)

    if not providers_list:
        raise HTTPException(status_code=404, detail="No products found")
    
    return providers_list

@router.get("/providers/{provider_id}")
def read_provider(provider_id: str):
    provider = collection.find_one({"_id": ObjectId(provider_id)})

    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider["id"] = str(provider["_id"])  
    del provider["_id"]  
    return provider


@router.post("/providers")
def create_provider(provider: Provider):
    provider_dict = provider.dict()
    provider_dict["created_at"] = datetime.utcnow()
    provider_dict["updated_at"] = datetime.utcnow()

    result = collection.insert_one(provider_dict)

    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Provider could not be created")

    return {"id": str(result.inserted_id)}

@router.post("/providers/multiple")
def create_providers(providers: List[Provider]):
    providers_dict = []
    for provider in providers:
        provider_dict = provider.dict()
        provider_dict["created_at"] = datetime.utcnow()
        provider_dict["updated_at"] = datetime.utcnow()
        providers_dict.append(provider_dict)

    result = collection.insert_many(providers_dict)

    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Providers could not be created")

    return {"ids": [str(inserted_id) for inserted_id in result.inserted_ids]}


@router.put("/providers/{provider_id}")
def update_provider(provider_id: str, provider: Provider):
    old_provider = collection.find_one({"_id": ObjectId(provider_id)})

    if old_provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider_dict = provider.dict()
    provider_dict["updated_at"] = datetime.utcnow()
    
    # Actualizar el proveedor en la colección
    result = collection.update_one({"_id": ObjectId(provider_id)}, {"$set": provider_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Provider could not be updated")

    # Recuperar el documento actualizado
    updated_provider = collection.find_one({"_id": ObjectId(provider_id)})
    updated_provider["id"] = str(updated_provider["_id"])
    del updated_provider["_id"]

    return updated_provider

@router.delete("/providers/{provider_id}")
def delete_provider(provider_id: str):
    provider = collection.find_one({"_id": ObjectId(provider_id)})

    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")

    collection.delete_one({"_id": ObjectId(provider_id)})
    return {"message": f"provider with the id '{provider_id}' was deleted"}
