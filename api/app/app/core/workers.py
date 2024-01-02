import uuid
import asyncio
import csv
from redis.asyncio import Redis
from datetime import datetime
from pydantic import ValidationError
from app.core.http_session import SessionMaker
from app.crud.redis_crud_base import crud_data
from app.schemas.scheme_data import UserIn, UserOut, Data
from app.schemas.constraint import ProcessingResult
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
        self._uuid: str = str(uuid_id)
        self.redis_db = redis_db
        self.data = data
        self.num_of_workers: int = 0
        self.to_process: list[asyncio.Task] = []

    async def worker(self) -> None:
        """Work with querie"""

        async with self.sem:
            print(self.sem._value)
            job = await self.queue.get()
            print('job')

            if self.sem._value == settings.SEMAPHORE-1:
                self.dt_start = datetime.utcnow()
                print(f'{self.dt_start=}')

            if self.sem._value == 0:
                print('lock')
                timeout = 1 - (datetime.utcnow() - self.dt_start).total_seconds()
                print(f'{timeout=}')
                if timeout > 0:
                    await asyncio.sleep(timeout)
                    print('sleep')

            print('release')
            await job
            print('done')
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

        await crud_data.set_field(self._uuid, self.redis_db, result)

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
                self.num_of_workers += 1
            except ValidationError:
                done['errors'] += 1
            done['data_in'] += 1

        await crud_data.update_fields(self._uuid, self.redis_db, done)

    async def run_work(self) -> None:
        """Run workers
        """
        await crud_data.create(self._uuid, self.redis_db, Data())
        await self.parse_data()
        self.tasks = [
            asyncio.create_task(self.worker())
            for _
            in range(self.num_of_workers)
                    ]
        import time
        start = time.time()
        await asyncio.gather(*self.tasks)
        end = time.time()
        print((end - start)  % 60)
