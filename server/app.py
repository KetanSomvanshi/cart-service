#!/usr/bin/env python3
import uvicorn
from controller import status, user_controller, customer_controller
from fastapi import FastAPI, Depends

from logger import logger
from models.user import UserRole
from server.auth import authenticate_token

app = FastAPI()
app.include_router(status.router)
app.include_router(user_controller.user_router)
#  token based authentication apis should have dependency on authenticate_token
app.include_router(customer_controller.customer_router, dependencies=[Depends(authenticate_token)])


@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=9999, reload=True)
