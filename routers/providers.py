from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo.collection import Collection
from bson.objectid import ObjectId
from datetime import datetime
from database import db

router = APIRouter()

collection: Collection = db["providers"]

class Provider(BaseModel):
    name: str
    address: str
    phone: str
    description: str

@router.get("/providers")
def read_providers():
    providers = collection.find()
    providers_list = []
    for provider in providers:
        provider["id"] = str(provider["_id"])  
        del provider["_id"]  
        providers_list.append(provider)

    if not providers_list:
        raise HTTPException(status_code=404, detail="No providers found")
    
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
