import uuid
from redis.asyncio import Redis
from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
    BackgroundTasks,
        )
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.uploades import upload_file
from app.schemas.constraint import MultipartType
from app.schemas.scheme_data import UsersOut
from app.crud.redis_crud_base import crud_data
from app.db.init_redis import get_redis_connection
from app.core.workers import Worker
from app.config import settings


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get(
    '/file',
    status_code=status.HTTP_200_OK,
    summary='Web form html sender',
    responses=settings.ERRORS,  # type: ignore
    response_class=HTMLResponse,
        )
async def get_form(request: Request):
    """Web form html sender
    # TODO: test me
    """
    return templates.TemplateResponse(
        "form_page.html",
        {"request": request, "path": settings.API_V1}
            )


@router.post(
    '/file',
    status_code=status.HTTP_201_CREATED,
    summary='Receive one file',
    responses=settings.ERRORS,  # type: ignore
        )
async def get_file(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Redis = Depends(get_redis_connection),
    uuid_id: uuid.UUID = Depends(uuid.uuid4),
        ):
    """Receive one file
    # TODO: test me
    """
    # upload files
    data = await upload_file(request)
    resp = {
        "request": request,
        "uuid_id": str(uuid_id),
        'done': False if data.multipart_content_type
        != MultipartType.CSV.value else True,
            }

    # work
    worker = Worker(uuid_id, db, data.value.decode("utf-8"))
    background_tasks.add_task(worker.run)

    # return result
    return templates.TemplateResponse(
        "file_done.html",
        resp,
        status_code=201
            )


@router.get(
    '/file/check',
    status_code=status.HTTP_200_OK,
    summary='Check file processing result',
    responses=settings.ERRORS,  # type: ignore
    response_class=HTMLResponse,
        )
async def check_result(
    request: Request,
    uuid_id: str,
    db: Redis = Depends(get_redis_connection)
        ):
    """Check file processing result
    # TODO: test me
    """
    result = await crud_data.get_status(uuid_id, db)

    return templates.TemplateResponse(
        "check_result.html",
        {
            "request": request,
            **result.model_dump(),
                }
            )


@router.get(
    '/file/download',
    status_code=status.HTTP_200_OK,
    summary='Get result json file',
    responses=settings.ERRORS,  # type: ignore
        )
async def getk_result(
    uuid_id: str,
    db: Redis = Depends(get_redis_connection)
        ) -> UsersOut:
    """Get result json file
    # TODO: test me
    """
    return await crud_data.get_result(uuid_id, db)
