from pymongo import MongoClient

#client = MongoClient("mongodb://localhost:27017/")
client = MongoClient("mongodb+srv://gaedwin92:gsQOnWybUUmSoTx1@cluster0.gynwpry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["technical_evaluation"]
