from fastapi import FastAPI

from car_api.routers import (
    user_routers, 
    brands_routes,
    car_routes
)

app = FastAPI()

app.include_router(user_routers)
app.include_router(brands_routes)
app.include_router(car_routes)
