#!/usr/bin/env python3
import uvicorn
from controller import status, user_controller, customer_controller
from fastapi import FastAPI, Depends

from logger import logger
from models.user import UserRole
from server.auth import authenticate_token
import http
import json

from pydantic import ValidationError

from controller.context_manager import context_log_meta, context_api_id
from logger import logger
from models.base import GenericResponseModel
from utils.exceptions import AppException
from utils.helper import build_api_response
from fastapi import FastAPI, Depends, Request
from sqlalchemy.exc import ProgrammingError, DataError, IntegrityError

app = FastAPI()

#  register routers here and add dependency on authenticate_token if token based authentication is required
app.include_router(status.router)
app.include_router(user_controller.user_router)
#  token based authentication apis should have dependency on authenticate_token
app.include_router(customer_controller.customer_router, dependencies=[Depends(authenticate_token)])


#  register exception handlers here
@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc):
    logger.error(extra=context_log_meta.get(), msg=f"data validation failed {exc.errors()}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                                   error=exc.errors()))


@app.exception_handler(ProgrammingError)
async def sql_exception_handler(request: Request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   error="Internal Server Error"))


@app.exception_handler(DataError)
async def sql_data_exception_handler(request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql data exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   error="Data Error for data provided"))


@app.exception_handler(AppException)
async def application_exception_handler(request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"application exception occurred error: {json.loads(str(exc))}")
    return build_api_response(GenericResponseModel(status_code=exc.status_code,
                                                   error=exc.message))


@app.exception_handler(IntegrityError)
async def sql_integrity_exception_handler(request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql integrity exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   error="Integrity Error for data provided"))


# register event handlers here
@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=9999, reload=True)
