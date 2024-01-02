from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from starlette.requests import ClientDisconnect
from fastapi import Request, HTTPException


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
