import http

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from data_adapter.db import db_engine

router = APIRouter(tags=["health_checks", "status"])


#  health check endpoints
@router.get("/status", status_code=http.HTTPStatus.OK)
async def status_check():
    return JSONResponse(status_code=http.HTTPStatus.OK, content={"status": "OK"})


@router.get("/deepstatus", status_code=http.HTTPStatus.OK)
async def deep_status_check():
    is_db_ok = db_engine.execute("select 'true'").cursor.fetchone()[0]
    if not is_db_ok:
        return JSONResponse(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                            content={'error': "db not connected"})
    return JSONResponse(status_code=http.HTTPStatus.OK, content={'db': is_db_ok})
