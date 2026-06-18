# from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from routes.fetch import router as fetch_router
from routes.search import router as search_router
from contextlib import asynccontextmanager
from db import init_db, SessionLocal
# from seed import seed
import asyncio
from core.logging import *
import logging

log = logging.getLogger(__name__)

# executor = ThreadPoolExecutor(max_workers=1)

# def run_seed():
#     db = SessionLocal()
#     try:
#         seed(db)
#     finally:
#         db.close()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     init_db()

#     loop = asyncio.get_event_loop()
#     loop.run_in_executor(None, run_seed)
#     yield


app = FastAPI()

app.include_router(fetch_router)

app.include_router(search_router)