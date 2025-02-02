import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import providers, products

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Métodos permitidos
    allow_headers=["*"],  # Headers permitidos
)

app.include_router(providers.router)
app.include_router(products.router)

# Ruta raíz
@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
