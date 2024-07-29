from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import providers, products

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Métodos permitidos
    allow_headers=["*"],  # Headers permitidos
)

app.include_router(providers.router)
app.include_router(products.router)
