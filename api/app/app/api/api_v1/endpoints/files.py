import uuid
from redis.asyncio import Redis
from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
        )
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.uploades import upload_file
from app.schemas.constraint import MultipartType
from app.db.init_redis import get_redis_connection
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

    # work
    worker = Worker(uuid_id, redis_db, data.value.decode("utf-8"))
    await worker.run_work()

    # return result
    return templates.TemplateResponse(
        "file_done.html",
        resp,
        status_code=201
            )
