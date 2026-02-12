from fastapi import FastAPI

from car_api.routers.users import user_routers

app = FastAPI()

app.include_router(user_routers)

