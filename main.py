from fastapi import FastAPI
from core.database import engine
from contextlib import asynccontextmanager
from core.database import create_db
from main_routes import api_router
from fastapi.middleware.cors import CORSMiddleware   # ← add this import
from fastapi.openapi.utils import get_openapi


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 Startup logic
    create_db()
    print("DB initialized")

    yield  # app runs here
    # 🛑 Shutdown logic (optional)
    print("App shutting down")

app = FastAPI(lifespan=lifespan)

# ── CORS — must be added BEFORE include_router ───────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],   # your Angular URL
    allow_credentials=True,
    allow_methods=["*"],                       # GET, POST, PUT, DELETE etc.
    allow_headers=["*"],                       # Authorization, Content-Type etc.
)


# ✅ Custom OpenAPI schema with Bearer token support
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title       = "Chat Application API",
        version     = "1.0.0",
        description = "API documentation",
        routes      = app.routes,
    )

    # ✅ Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type"         : "http",
            "scheme"       : "bearer",
            "bearerFormat" : "JWT"
        }
    }

    # ✅ Apply security globally to all routes
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


app.include_router(api_router)

