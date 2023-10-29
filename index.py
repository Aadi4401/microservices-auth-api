from fastapi import FastAPI
# from routes.user import user,auth_router
from routes.user import *
app = FastAPI()


app.include_router(user)
app.include_router(Login)
app.include_router(reset)
app.include_router(userupdate)
# app.include_router(auth_router)
