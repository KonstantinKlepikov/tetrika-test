# import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.api_v1.api import api_router


# from logging import FileHandler, DEBUG

# log = logging.getLogger('uvicorn')


# class DebugFileHandler(FileHandler):
#     def __init__(self, filename, mode='a', encoding=None, delay=False)
#         super().__init__(filename, mode, encoding, delay)

#     def emit(self, record):
#         if not record.levelno == DEBUG:
#             return
#         super().emit(record)

# log.addHandler(DebugFileHandler())

# loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
# print(loggers)


app = FastAPI(
    title=settings.title,
    openapi_url=f"{settings.API_V1}/openapi.json",
    description=settings.descriprion,
    version=settings.version,
    openapi_tags=settings.openapi_tags,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1)
