import csv
import uuid
import asyncio
from redis.asyncio import Redis
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from starlette.requests import ClientDisconnect
from pydantic import ValidationError
from fastapi import Request, HTTPException
from app.schemas import scheme_data
from app.schemas.constraint import ProcessingResult
from app.core.workers import workers
from app.config import settings


async def upload_file(request: Request) -> ValueTarget:
    """Upload file stream
    # TODO: test me
    """
    try:
        data = ValueTarget()
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', data)
        async for chunk in request.stream():
            parser.data_received(chunk)
    except ClientDisconnect:
        raise HTTPException(
            status_code=400,
            detail='Client dicsonnected.'
                )

    return data


async def run_workers() -> None:
    """Run workers
    """
    tasks = [
        asyncio.create_task(workers.worker())
        for _
        in range(settings.WORKERS)
                ]
    await asyncio.wait(tasks)


def parse_data(
    data: str,
    uuid_id: uuid.UUID
        ) -> tuple[dict[str, int], list[scheme_data.UserIn]]:

    done = {'data_in': 0,'errors': 0, }
    to_process = []

    reader = csv.DictReader(data.splitlines())
    for row in reader:
        try:
            to_process.append(scheme_data.UserIn(**row)) # TODO: ditectly to queue
        except ValidationError:
            done['errors'] += 1
        done['data_in'] += 1

    return done, to_process # TODO: remove to_process
