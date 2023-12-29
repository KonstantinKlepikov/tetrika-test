import csv
import uuid
from redis.asyncio import Redis
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from starlette.requests import ClientDisconnect
from pydantic import ValidationError
from fastapi import Request, HTTPException
from app.schemas import scheme_data
from app.schemas.constraint import ProcessingResult


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


def parse_data(
    data: str,
    uuid_id: uuid.UUID
        ) -> tuple[scheme_data.DataOut, list[scheme_data.UserIn]]:

    done = {'uuid_id': uuid_id, 'data_in': 0,'errors': 0, }
    to_process = []

    reader = csv.DictReader(data.splitlines())
    for row in reader:
        try:
            to_process.append(scheme_data.UserIn(**row))
        except ValidationError:
            done['errors'] += 1
        done['data_in'] += 1

    return scheme_data.DataOut(**done), to_process # TODO: to_process add ditectly ro queue


async def make_resources(
    data: str,
    redis_db: Redis,
    uuid_id: str
        ) -> None:
    """Make resources from file
    # TODO: test me
    """
