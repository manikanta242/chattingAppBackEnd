from fastapi import FastAPI
from core.database import engine
import auth.models
import auth.routes

app = FastAPI()
auth.models.Base.metadata.create_all(bind=engine)

app.include_router(auth.routes.router)

