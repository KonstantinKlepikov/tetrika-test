import uuid
from redis.asyncio import Redis
from fastapi import (
    APIRouter,
    status,
    Request,
    BackgroundTasks,
    Depends,
        )
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.uploades import upload_file, make_resources
from app.schemas.constraint import MultipartType
from app.db.init_redis import get_redis_connection
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
    background_tasks: BackgroundTasks,
    redis_db: Redis = Depends(get_redis_connection),
        ) -> HTMLResponse:
    """Receive one file
    """
    # upload files
    data = await upload_file(request)
    resp = {
        "request": request,
        "path": settings.API_V1+'/file',
        "uuid_id": (uuid_id := str(uuid.uuid4())),
        'done': False if data.multipart_content_type \
                != MultipartType.CSV else True,
            }

    # add to redis id


    # parse data
    background_tasks.add_task(
        make_resources,
        data.value,
        redis_db,
        uuid_id
            )

    return templates.TemplateResponse(
        "file_done.html",
        resp, status_code=201
            )
