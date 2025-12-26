from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import Base, engine
from routes_auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="3-Level Image Password Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ade-login.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
