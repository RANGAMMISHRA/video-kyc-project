# backend/utils/performance_utils.py
import time
import functools
import logging

# Setup logger
logger = logging.getLogger("performance")
handler = logging.FileHandler("performance_log.txt")
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"{func.__name__} executed in {elapsed:.2f} seconds")
        return result
    return wrapper
 