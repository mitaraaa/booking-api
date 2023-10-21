from fastapi import FastAPI

import routers

app = FastAPI()

for router in routers.__all__:
    app.include_router(getattr(routers, router))
