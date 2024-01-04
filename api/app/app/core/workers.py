import uuid
import asyncio
import csv
from redis.asyncio import Redis
from pydantic import ValidationError
from fastapi.logger import logger as fastapi_logger
from app.core.http_session import SessionMaker
from app.crud.redis_crud_base import crud_data
from app.schemas.scheme_data import UserIn, UserOut
from app.schemas.constraint import ProcessingResult
from app.util.timer import timer
from app.config import settings


class Worker:
    """Worker for parsing data
    # TODO: test me
    """
    session_maker: SessionMaker = SessionMaker

    def __init__(
        self,
        uuid_id: uuid.UUID,
        db: Redis,
        data: str
            ) -> None:
        self.uuid_id = uuid_id
        self.db = db
        self.data = data
        self._uuid_id: str = str(uuid_id)

        fastapi_logger.debug(f'Worker uuid_id={self._uuid_id} is created.')

    async def query_and_push(self, user_in: UserIn) -> None:
        """Query external api and push result to redis

        Args:
            data (UserIn): user in data
        """
        try:
            result = await self.session_maker.post(settings.PL_URL, user_in)
            result = UserOut(
                postId=result['id'],
                result=ProcessingResult.DONE,
                userId=result['userId']
                    )
            fastapi_logger.debug(f'{result}')
        except (ValidationError, ConnectionRefusedError):
            result = UserOut(userId=user_in.userId)
            fastapi_logger.debug(f'{result}')

        await crud_data.set_field(self._uuid_id, self.db, result)

    @timer
    async def run(self) -> None:
        """Run worker
        """
        done = {'data_in': 0,'errors': 0, }
        to_process = []
        reader = csv.DictReader(self.data.splitlines())

        for row in reader:
            try:
                to_process.append(
                    asyncio.create_task(self.query_and_push(UserIn(**row)))
                        )
            except ValidationError:
                done['errors'] += 1
            done['data_in'] += 1

        fastapi_logger.debug(f'{done}')

        await crud_data.update_fields(self._uuid_id, self.db, done)
        await asyncio.gather(*to_process)
