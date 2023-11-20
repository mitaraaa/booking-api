import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routers

load_dotenv()

app = FastAPI()

allow_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    os.environ.get("WEBSITE_URL"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

for router in routers.__all__:
    app.include_router(getattr(routers, router))
