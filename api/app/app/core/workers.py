import asyncio
from asyncio import Semaphore, Queue
from datetime import datetime
from app.config import settings


class Workers:
    """Workers to do some periodic job
    """
    queue: Queue | None = None
    sem: Semaphore | None = None

    def __init__(self, num_of_workers: int = settings.WORKERS) -> None:
        self.num_of_workers = num_of_workers

    @classmethod
    def _set_all(cls) -> None:
        """Set empty queue and workers
        """
        if cls.queue is None:
            cls.queue = Queue()
        if cls.sem is None:
            cls.sem = Semaphore(settings.SEMAPHORE)

    async def worker(self) -> None:
        """Work with querie"""

        self._set_all()
        while True:

            job = await self.queue.get()

            async with self.sem:

                if self.sem._value == settings.SEMAPHORE+1:
                    self.dt_start = datetime.utcnow()

                if self.sem._value == 0:
                    timeout = 1 - (datetime.utcnow() - self.dt_start).total_seconds()
                    if timeout > 0:
                        await asyncio.sleep(timeout)
                        if self.sem.locked():
                            self.sem.release()

            await job
            self.queue.task_done()


workers = Workers()
