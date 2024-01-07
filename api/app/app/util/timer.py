import functools
import time
from typing import Callable, Coroutine, Any
from fastapi.logger import logger as fastapi_logger


def timer(func: Callable) -> Callable:
    """Async time measure decoretor
    # TODO: test me
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Coroutine[Any, None, None]:

        fastapi_logger.debug(f'Dtarting {func} with args {args} {kwargs}')
        start = time.time()

        try:
            return await func(*args, **kwargs)

        finally:
            end = time.time()
            total = end - start
            fastapi_logger.debug(f'Finished {func} in {total:.4f} second(s)')

    return wrapper
