from fastapi import FastAPI
from routers import providers, products

app = FastAPI()

app.include_router(providers.router)
app.include_router(products.router)
