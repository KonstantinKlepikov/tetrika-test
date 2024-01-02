import uuid
import asyncio
from redis.asyncio import Redis
from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
        )
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.uploades import upload_file, parse_data
from app.schemas.constraint import MultipartType
from app.schemas import scheme_data
from app.crud.redis_crud_base import crud_data
from app.db.init_redis import get_redis_connection
from app.core.http_session import SessionMaker
from app.core.workers import Worker
from app.config import settings


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get(
    '/file',
    status_code=status.HTTP_200_OK,
    summary='Web form html sender',
    responses=settings.ERRORS,
    response_class=HTMLResponse,
        )
async def get_form(request: Request) -> HTMLResponse:
    """Web form html sender
    """
    return templates.TemplateResponse(
        "form_page.html",
        {"request": request, "path": settings.API_V1+'/file'}
            )

import random

async def s():
    await asyncio.sleep(random.randint(0, 4)/10)

@router.post(
    '/file',
    status_code=status.HTTP_201_CREATED,
    summary='Receive one file',
    responses=settings.ERRORS,
        )
async def get_file(
    request: Request,
    redis_db: Redis = Depends(get_redis_connection),
    uuid_id: uuid.UUID = Depends(uuid.uuid4),
        ) -> HTMLResponse:
    """Receive one file
    """
    # upload files
    data = await upload_file(request)
    resp = {
        "request": request,
        "path": settings.API_V1+'/file',
        "uuid_id": str(uuid_id),
        'done': False if data.multipart_content_type \
                != MultipartType.CSV.value else True,
            }

    # add to redis id
    await crud_data.create(uuid_id, redis_db, scheme_data.Data())

    # parse data
    done, to_process = parse_data(data.value.decode("utf-8"), uuid_id)
    del data

    await crud_data.update_fields(uuid_id, redis_db, done)

    # query
    tasks = [s for _ in to_process]
    worker = Worker(tasks)
    await worker.run_workers()

    # return result
    return templates.TemplateResponse(
        "file_done.html",
        resp,
        status_code=201
            )
