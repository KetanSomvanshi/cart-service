import http
import json

from pydantic import ValidationError

from controller.context_manager import context_log_meta, context_api_id
from logger import logger
from models.base import GenericResponseModel
from server.app import app
from utils.exceptions import AppException
from utils.helper import build_api_response
from fastapi import FastAPI, Depends, Request
from sqlalchemy.exc import ProgrammingError, DataError, IntegrityError


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc):
    logger.error(extra=context_log_meta.get(), msg=f"data validation failed {exc.errors()}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, api_id=context_api_id.get(),
                                                   error=exc.errors()))


@app.exception_handler(ProgrammingError)
async def sql_exception_handler(request: Request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   api_id=context_api_id.get(), error=exc.errors()))


@app.exception_handler(DataError)
async def sql_data_exception_handler(request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql data exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   api_id=context_api_id.get(), error=exc.errors()))


@app.exception_handler(AppException)
def application_exception_handler(request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"application exception occurred error: {json.loads(str(exc))}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   api_id=context_api_id.get(), error=exc.message))


@app.exception_handler(IntegrityError)
async def sql_integrity_exception_handler(request, exc):
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql integrity exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   api_id=context_api_id.get(), error=exc.errors()))
