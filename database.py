from pymongo import MongoClient
import certifi

#client = MongoClient("mongodb://localhost:27017/")

MONGO_DETAILS = "mongodb+srv://gaedwin92:gsQOnWybUUmSoTx1@cluster0.gynwpry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_DETAILS, tlsCAFile=certifi.where())

db = client["technical_evaluation"]
