import functools
import time
from typing import Callable, Any
from fastapi.logger import logger as fastapi_logger


def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        fastapi_logger.debug(f'starting {func} with args {args} {kwargs}')
        start = time.time()
        try:
            return await func(*args, **kwargs)
        finally:
            end = time.time()
            total = end - start
            fastapi_logger.debug(f'finished {func} in {total:.4f} second(s)')
    return wrapper
