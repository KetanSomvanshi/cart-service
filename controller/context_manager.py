from contextvars import ContextVar

import uuid
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from data_adapter.db import get_db
from logger import logger
from models.user import UserTokenData

# we are using context variables to store request level context , as FASTAPI
# does not provide request context out of the box
context_db_session: ContextVar[Session] = ContextVar('db_session', default=None)
context_api_id: ContextVar[str] = ContextVar('api_id')
context_log_meta: ContextVar[dict] = ContextVar('log_meta', default={})
context_user_id: ContextVar[str] = ContextVar('user_id', default=None)
context_actor_user_data: ContextVar[UserTokenData] = ContextVar('actor_user_data', default=None)


async def build_request_context(request: Request,
                                db: Session = Depends(get_db)):
    # set the db-session in context-var so that we don't have to pass this dependency downstream
    context_db_session.set(db)
    context_api_id.set(str(uuid.uuid4()))
    context_user_id.set(request.headers.get('X-User-ID'))
    context_log_meta.set({'api_id': context_api_id.get(), 'request_id': request.headers.get('X-Request-ID'),
                          'user_id': context_user_id.get(), 'actor': context_actor_user_data.get()})
    logger.info(extra=context_log_meta.get(), msg="REQUEST_INITIATED")


def get_db_session() -> Session:
    return context_db_session.get()
