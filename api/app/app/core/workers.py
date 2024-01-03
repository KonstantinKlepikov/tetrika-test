import uuid
import asyncio
import csv
from redis.asyncio import Redis
from datetime import datetime
from pydantic import ValidationError
from fastapi.logger import logger as fastapi_logger
from app.core.http_session import SessionMaker
from app.crud.redis_crud_base import crud_data
from app.schemas.scheme_data import UserIn, UserOut, Data
from app.schemas.constraint import ProcessingResult
from app.util.timer import timer
from app.config import settings


class Worker:
    """Workers for some periodic job

    # TODO: test me
    """
    sem: asyncio.Semaphore = asyncio.Semaphore(settings.SEMAPHORE)
    queue: asyncio.Queue = asyncio.Queue()
    session_maker: SessionMaker = SessionMaker

    def __init__(
        self,
        uuid_id: uuid.UUID,
        redis_db: Redis,
        data: str
            ) -> None:
        self.uuid_id = uuid_id
        self._uuid_id: str = str(uuid_id)
        self.redis_db = redis_db
        self.data = data
        self._num_of_workers: int = 0
        fastapi_logger.debug(f'Worker uuid_id={self._uuid_id} is created.')

    async def worker(self) -> None:
        """Work with querie"""

        fastapi_logger.debug('Start worker.')

        async with self.sem:
            fastapi_logger.debug(self.sem._value)
            job = await self.queue.get()
            fastapi_logger.debug('Job get by worker.')

            if self.sem._value == settings.SEMAPHORE-1:
                self.dt_start = datetime.utcnow()
                fastapi_logger.debug(f'Is set dt_start to {self.dt_start.strftime("%M:%S:%f")}')

            if self.sem._value == 0:
                timeout = 1 - (datetime.utcnow() - self.dt_start).total_seconds()
                fastapi_logger.debug(f'Calculated lock {timeout}.')
                if timeout > 0:
                    await asyncio.sleep(timeout)
                    fastapi_logger.debug('Sleep with lock.')

            fastapi_logger.debug('Make job.')
            await job
            fastapi_logger.debug('Job is done')
            self.queue.task_done()

    async def push_data(
        self,
        user_in: UserIn,
            ) -> None:
        """_summary_

        Args:
            data (UserIn): _description_
            session_maker (SessionMaker, optional): _description_. Defaults to SessionMaker.
        """
        try:
            result = await self.session_maker.post(settings.PL_URL, user_in)
            result = UserOut(
                postId=result['id'],
                result=ProcessingResult.DONE,
                userId=result['userId']
                    )
        except (ValidationError, ConnectionRefusedError):
            result = UserOut(userId=user_in.userId)

        await crud_data.set_field(self._uuid_id, self.redis_db, result)

    @timer
    async def parse_data(self) -> None:
        """_summary_
        """
        done = {'data_in': 0,'errors': 0, }
        reader = csv.DictReader(self.data.splitlines())

        for row in reader:
            try:
                self.queue.put_nowait(
                    asyncio.create_task(self.push_data(UserIn(**row)))
                        )
                self._num_of_workers += 1
            except ValidationError:
                done['errors'] += 1
            done['data_in'] += 1

        await crud_data.update_fields(self._uuid_id, self.redis_db, done)

    @timer
    async def run_work(self) -> None:
        """Run workers
        """
        await crud_data.create(self._uuid_id, self.redis_db, Data())
        await self.parse_data()
        self.tasks = [
            asyncio.create_task(self.worker())
            for _
            in range(self._num_of_workers)
                    ]
        # import time
        # start = time.time()
        await asyncio.gather(*self.tasks)
        # end = time.time()
        # fastapi_logger.debug((end - start)  % 60)
