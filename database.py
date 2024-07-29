import logging
from pymongo import MongoClient
import certifi

logging.basicConfig(level=logging.INFO)

MONGO_DETAILS = "mongodb+srv://gaedwin92:gsQOnWybUUmSoTx1@cluster0.gynwpry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
try:
    client = MongoClient(MONGO_DETAILS, tlsCAFile=certifi.where())
    db = client["technical_evaluation"]
    logging.info("Successfully connected to MongoDB")
except Exception as e:
    logging.error("Could not connect to MongoDB", exc_info=True)
