from typing import Annotated
from fastapi import APIRouter, status, Form, UploadFile, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
path_to_file = settings.API_V1+'/file'


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
        {"request": request, "path": path_to_file}
            )


@router.post(
    '/file',
    status_code=status.HTTP_303_SEE_OTHER,
    summary='Receive one file',
    responses=settings.ERRORS,
        )
async def get_file(
    request: Request,
    file: Annotated[UploadFile, Form()]
        ) -> RedirectResponse:
    """Receive one file
    """
    # aiofile async gen here

    url = request.url_for('get_form')
    return RedirectResponse(
        url,
        status_code=status.HTTP_303_SEE_OTHER
            )
