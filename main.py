from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import create_db
from main_routes import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    print("DB initialized")
    yield
    print("App shutting down")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

@app.get("/")
def root():
    return {"status": "running ✅"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title       = "Chat Application API",
        version     = "1.0.0",
        description = "API documentation",
        routes      = app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type"        : "http",
            "scheme"      : "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"✅ Starting on port: {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)