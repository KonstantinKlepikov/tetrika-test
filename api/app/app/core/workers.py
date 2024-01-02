import asyncio
from typing import Iterable, Coroutine
from datetime import datetime
from app.config import settings


class Worker:
    """Workers for some periodic job
    """
    sem: asyncio.Semaphore = asyncio.Semaphore(settings.SEMAPHORE)

    def __init__(self, data: Iterable[Coroutine]) -> None:
        self.num_of_workers = len(data)
        self.queue: asyncio.Queue = asyncio.Queue()
        for i in data:
            self.queue.put_nowait(i)

    async def worker(self) -> None:
        """Work with querie"""

        job = await self.queue.get()
        print('job')

        # async with self.sem:
        #     print(self.sem._value)

        #     if self.sem._value == settings.SEMAPHORE-1:
        #         self.dt_start = datetime.utcnow()
        #         print(f'{self.dt_start=}')

        #     if self.sem._value == 0:
        #         print('lock')
        #         timeout = 1 - (datetime.utcnow() - self.dt_start).total_seconds()
        #         print(f'{timeout=}')
        #         if timeout > 0:
        #             await asyncio.sleep(timeout)
        #             print('sleep')
        #             if self.sem.locked():
        #                 self.sem.release()
        #                 print('release')

        #     await job()
        #     print('done')
        #     self.queue.task_done()
        async with self.sem:
            print(self.sem._value)

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
            await job()
            print('done')
            self.queue.task_done()

    async def run_workers(self) -> None:
        """Run workers
        """
        self.tasks = [
            asyncio.create_task(self.worker())
            for _
            in range(self.num_of_workers)
                    ]
        await asyncio.gather(*self.tasks)
