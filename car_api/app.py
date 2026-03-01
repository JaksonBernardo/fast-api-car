from fastapi import FastAPI

from car_api.routers import (
    user_routers, 
    brands_routers,
    car_routers,
    auth_routers
)

app = FastAPI()

app.include_router(auth_routers)
app.include_router(user_routers)
app.include_router(brands_routers)
app.include_router(car_routers)
